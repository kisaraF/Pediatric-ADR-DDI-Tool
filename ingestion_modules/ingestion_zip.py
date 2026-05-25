import requests
import requests.exceptions as req_err
from io import BytesIO
from zipfile import ZipFile
from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql.functions import col, sha2, concat_ws, current_timestamp
from fetch_http_link import operation
from pediatric_adr_shared.logging_mod import init_logger
import os
import json
from concurrent.futures import ThreadPoolExecutor
import subprocess
from functools import partial, reduce


logger = init_logger()


def sparkSession() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def readFile(ss: SparkSession, url, mode: int = 1) -> dict:
    logger.info(f"Processing starting for {url}...")
    reserved_words = ["DEMO", "DRUG", "OUTC", "REAC"]

    if mode == 2:
        with open(url, "rb") as bin_f:
            url = bin_f.read()

    with ZipFile(BytesIO(url)) as zip_file:
        chosen_files = [
            f
            for f in zip_file.namelist()
            if f.endswith(".txt") and any(word in f for word in reserved_words)
        ]

        master = {}

        for file in chosen_files:
            tb_ = file.split("/")[-1].split(".")[0]
            tb_id = tb_[:4].lower()

            df = pd.read_csv(zip_file.open(file), sep="$", dtype=str)
            logger.info(f"{file} loaded to pandas {df.shape}")

            spark_df = ss.createDataFrame(df)
            logger.info(f"{file} Loaded as a Spark DataFrame")

            spark_df = spark_df.withColumn(
                "_hash_id",
                sha2(concat_ws("||", *[col(c) for c in spark_df.columns]), 256),
            )

            spark_df = spark_df.withColumn("ingestion_timestamp", current_timestamp())
            logger.info("Added metadata columns")

            master[tb_id] = spark_df
        return master


def pull_data(url: str):
    try:
        logger.info("Extracting bytes from URL")
        # res = session.get(url, headers=headers, timeout=30)
        res = requests.get(url)
        res.raise_for_status()
        spark = sparkSession()
        logger.info("spark session created")
        readFile(spark, res.content)
    except req_err.HTTPError as http_err:
        logger.error(f"HTTP Error: {http_err}")
    except Exception as e:
        logger.error(f"Other error encountered: {e}")


def push_data(fp: str, ss: SparkSession):
    try:
        master = readFile(ss, fp, 2)
        master["url"] = fp
        master["status"] = "CF"
        return master
    except Exception as e:
        logger.error(f"Unexpected exception as {e}")


def curl_files(url: str):
    parent_path = "backfill-extracts"
    dest_path = f"{parent_path}/{url.split('/')[-1].lower()}"
    # check if file already exists or not before downloading
    if os.path.isdir(parent_path):
        x = [fi for fi in os.listdir(parent_path) if dest_path.split("/")[-1] in fi]
        if len(x) == 1:
            if os.path.getsize(f"{parent_path}/{x[0]}") > 58 * 1024 * 1024:
                logger.info(f"Skipping as a {x[0]} exists and size is over 58 MB")
                return dest_path
        else:
            logger.info(f"Starting download for {dest_path.split('/')[-1]}...")
            cmd = [
                "curl",
                "--fail",  # exit non-zero on HTTP errors
                "--location",  # follow redirects
                "--silent",
                "--show-error",  # show errors even when silent
                "--retry",
                "3",
                "--retry-delay",
                "5",
                "--max-time",
                "600",
                "-o",
                dest_path,
                url,
            ]
            subprocess.run(cmd)
            logger.info(f"Downloaded {dest_path.split('/')[-1]}")
            return dest_path
    else:
        logger.error(f"{parent_path} is not a directory")


def bulk_load(fn: str):
    spark = sparkSession()
    logger.info("spark session created")

    try:
        with open(fn, "r", encoding="utf-8") as fr:
            data = json.load(fr)

        unresolved_items = [
            i for i in data if i["status"] == "NF"
        ]  # Status = "NF" (Not Fetched) | Status = "CF" (Completed Fetching)
        unresolved_links = [j["link"] for j in unresolved_items]
        logger.info(f"Found {len(unresolved_links)} links to bulk update")

        partial_push = partial(push_data, ss=spark)
        with ThreadPoolExecutor(max_workers=4) as executors:
            dests = list(executors.map(curl_files, unresolved_links))
            completion_status = list(executors.map(partial_push, dests))
            logger.info("DataFrames retrieved. Combining process started...")

        demo_dfs = [d["demo"] for d in completion_status]
        drug_dfs = [d["drug"] for d in completion_status]
        reac_dfs = [d["reac"] for d in completion_status]
        outc_dfs = [d["outc"] for d in completion_status]

        demo_df_combined = reduce(lambda a, b: a.union(b), demo_dfs)
        drug_df_combined = reduce(lambda a, b: a.union(b), drug_dfs)
        reac_df_combined = reduce(lambda a, b: a.union(b), reac_dfs)
        outc_df_combined = reduce(lambda a, b: a.union(b), outc_dfs)
        logger.info("Combining process finished. Starting to write to delta...")

        write_list = {
            "demo": demo_df_combined,
            "drug": drug_df_combined,
            "reac": reac_df_combined,
            "outc": outc_df_combined,
        }

        for tb_id, sdf in write_list.items():
            tb_name = f"pediatric_adr_events.raw_source.{tb_id}"
            sdf.writeTo(tb_name).append()

        logger.info("Completed fetching to delta table process")

        # update master tracking file
        for original_dict, updated_dict in zip(unresolved_items, completion_status):
            # validate correctly to update the correct file
            fmt_updt_url = updated_dict["url"].split("/")[-1].split("_")[-1]
            year_i, quarter_i = fmt_updt_url[:4], fmt_updt_url[5]
            if str(original_dict["year"]) == str(year_i) and str(
                original_dict["quarter"]
            ) == str(quarter_i):
                original_dict["status"] = updated_dict["status"]

        with open(fn, "w", encoding="utf-8") as fw:
            json.dump(data, fw, indent=4)
        logger.info("Completed updating json tracking file")
        # spark.stop()
    except KeyboardInterrupt:
        logger.error("Execution stopped by Kisara")
        # spark.interruptAll()
    except Exception as e:
        logger.error(f"Unexpected error -> {e}")
        # spark.interruptAll()


def ingest_data(mode: int):
    """
    mode:
    1 - load latest data by fetching the link from site
    2 - bulk-load the data through the given links
    """
    if mode == 1:
        url = operation()
        pull_data(url)

    if mode == 2:
        file_name = "bulk_load_data.json"
        bulk_load(file_name)


if __name__ == "__main__":
    ingest_data(mode=2)
