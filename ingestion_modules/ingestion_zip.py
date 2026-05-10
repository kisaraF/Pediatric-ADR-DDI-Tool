import requests, requests.exceptions as req_err
from io import BytesIO
from zipfile import ZipFile
from databricks.connect import DatabricksSession
import pandas as pd
from pyspark.sql.functions import col, sha2, concat_ws, current_timestamp
from fetch_http_link import operation


def sparkSession() -> DatabricksSession:
    spark = DatabricksSession.builder.serverless().profile("DEFAULT").getOrCreate()
    return spark


def checkStatus(url: str):
    res = requests.get(url)
    return res


def readFile(ss: DatabricksSession, url):
    print("Processing starting ...")
    reserved_words = ["DEMO", "DRUG", "OUTC", "REAC"]

    with ZipFile(BytesIO(url)) as zip_file:
        chosen_files = [
            f
            for f in zip_file.namelist()
            if f.endswith(".txt") and any(word in f for word in reserved_words)
        ]
        print(chosen_files)

        for file in chosen_files:
            print(f"\nProcessing {file}")

            tb_id = file.split("/")[-1].split(".")[0][:4].lower()
            tb_name = f"pediatric_adr_events.raw_source.{tb_id}"

            df = pd.read_csv(zip_file.open(file), sep="$", dtype=str)
            print(f"File loaded to pandas {df.shape}")

            spark_df = ss.createDataFrame(df)
            print("Loaded as a Spark DataFrame")

            spark_df = spark_df.withColumn(
                "_hash_id",
                sha2(concat_ws("||", *[col(c) for c in spark_df.columns]), 256),
            )

            spark_df = spark_df.withColumn("ingestion_timestamp", current_timestamp())
            print("Added metadata columns")

            spark_df.write.format("delta").mode("append").saveAsTable(tb_name)
            print("Loaded to Databricks")


if __name__ == "__main__":
    url = operation()
    print(f"Retrieved the URL: {url}")
    try:
        print("Extracting bytes from URL")
        res = requests.get(url)
        res.raise_for_status()
        spark = sparkSession()
        print("spark session created")
        readFile(spark, res.content)
        print(type(res.content))
    except req_err.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
    except Exception as e:
        print(f"Other error encountered: {e}")
