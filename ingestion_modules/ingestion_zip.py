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
from functools import partial


logger = init_logger()


def sparkSession() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def readFile(ss: SparkSession, url, mode: int = 1):
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

        for file in chosen_files:
            # logger.info(f"\nProcessing {file}")

            tb_id = file.split("/")[-1].split(".")[0][:4].lower()
            tb_name = f"pediatric_adr_events.raw_source.{tb_id}"

            df = pd.read_csv(zip_file.open(file), sep="$", dtype=str)
            logger.info(f"{file} loaded to pandas {df.shape}")

            spark_df = ss.createDataFrame(df)
            logger.info("Loaded as a Spark DataFrame")

            spark_df = spark_df.withColumn(
                "_hash_id",
                sha2(concat_ws("||", *[col(c) for c in spark_df.columns]), 256),
            )

            spark_df = spark_df.withColumn("ingestion_timestamp", current_timestamp())
            logger.info("Added metadata columns")

            spark_df.write.format("delta").mode("append").saveAsTable(tb_name)
            logger.info(f"{file} Loaded to Databricks")


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
        readFile(ss, fp, 2)
        return {"url": fp, "status": "CF"}
    except Exception as e:
        logger.error(f"Unexpected exception as {e}")


def curl_files(url: str):
    dest_path = f"backfill-extracts/{url.split('/')[-1].lower()}"
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


def bulk_load(fn: str):
    spark = sparkSession()
    logger.info("spark session created")

    with open(fn, "r", encoding="utf-8") as fr:
        data = json.load(fr)

    unresolved_items = [
        i for i in data if i["status"] == "NF"
    ]  # Status = "NF" (Not Fetched) | Status = "CF" (Completed Fetching)
    unresolved_links = [j["link"] for j in unresolved_items]
    logger.info(f"Found {len(unresolved_links)} links to bulk update")

    partial_curl = partial(push_data, ss=spark)
    with ThreadPoolExecutor(max_workers=4) as executors:
        # dests = list(executors.map(curl_files, unresolved_links))
        dests = [  # Files were already downloaded therefore, passing them as links temporarily
            "backfill-extracts/faers_ascii_2025q2.zip",
            "backfill-extracts/faers_ascii_2025q1.zip",
            "backfill-extracts/faers_ascii_2025q3.zip",
            "backfill-extracts/faers_ascii_2025q4.zip",
        ]
        completion_status = list(executors.map(partial_curl, dests))
    logger.info("Completed fetching to delta table process")

    # update master tracking file
    for original_dict, updated_dict in zip(unresolved_items, completion_status):
        # validate correctly to update the correct file
        fmt_updt_url = updated_dict["url"].split("/")[-1].split("_")[-1]
        year_i, quarter_i = fmt_updt_url[:4], fmt_updt_url[5]
        if original_dict["year"] == year_i and original_dict["quarter"] == quarter_i:
            original_dict["status"] = updated_dict["status"]

    with open(fn, "w", encoding="utf-8") as fw:
        json.dump(data, fw, indent=4)
    logger.info("Completed updating json tracking file")


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
