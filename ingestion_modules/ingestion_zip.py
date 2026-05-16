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


logger = init_logger()


def sparkSession() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def readFile(ss: SparkSession, url):
    logger.info("Processing starting ...")
    reserved_words = ["DEMO", "DRUG", "OUTC", "REAC"]

    with ZipFile(BytesIO(url)) as zip_file:
        chosen_files = [
            f
            for f in zip_file.namelist()
            if f.endswith(".txt") and any(word in f for word in reserved_words)
        ]

        for file in chosen_files:
            logger.info(f"\nProcessing {file}")

            tb_id = file.split("/")[-1].split(".")[0][:4].lower()
            tb_name = f"pediatric_adr_events.raw_source.{tb_id}"

            df = pd.read_csv(zip_file.open(file), sep="$", dtype=str)
            logger.info(f"File loaded to pandas {df.shape}")

            spark_df = ss.createDataFrame(df)
            logger.info("Loaded as a Spark DataFrame")

            spark_df = spark_df.withColumn(
                "_hash_id",
                sha2(concat_ws("||", *[col(c) for c in spark_df.columns]), 256),
            )

            spark_df = spark_df.withColumn("ingestion_timestamp", current_timestamp())
            logger.info("Added metadata columns")

            spark_df.write.format("delta").mode("append").saveAsTable(tb_name)
            logger.info("Loaded to Databricks")


def ingest_data():
    url = operation()
    try:
        logger.info("Extracting bytes from URL")
        res = requests.get(url)
        res.raise_for_status()
        spark = sparkSession()
        logger.info("spark session created")
        readFile(spark, res.content)
    except req_err.HTTPError as http_err:
        logger.error(f"HTTP Error: {http_err}")
    except Exception as e:
        logger.error(f"Other error encountered: {e}")


if __name__ == "__main__":
    ingest_data()
