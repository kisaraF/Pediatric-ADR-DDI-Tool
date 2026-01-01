import requests
from io import BytesIO
from zipfile import ZipFile
from databricks.connect import DatabricksSession
import pandas as pd
from pyspark.sql.functions import col, sha2, concat_ws, current_timestamp


# Constants
links = {
        "2025_q3":"https://fis.fda.gov/content/Exports/faers_ascii_2025q3.zip"
}

sample_file = "sample.zip"

def sparkSession() -> DatabricksSession:
    spark = DatabricksSession.builder.serverless().profile("DEFAULT").getOrCreate()
    return spark


def checkStatus(url: str):
    res = requests.head(url)

    msg = f"Response ok? {res.ok}! Status code -> {res.status_code}"
    print(msg)


def readFile(ss: DatabricksSession, url: str):
    reserved_words = ["DEMO", "DRUG", "OUTC", "REAC"]

    with open(url, 'rb') as bin_f:
        content = bin_f.read()

    with ZipFile(BytesIO(content)) as zip_file:
        chosen_files = [f for f in zip_file.namelist() if f.endswith('.txt') and any(word in f for word in reserved_words)]
        print(chosen_files)

        for file in chosen_files:
            print(f"\nProcessing {file}")
            
            tb_id = file.split("/")[-1].split(".")[0][:4].lower()
            tb_name = f"pediatric_adr_events.raw_source.{tb_id}"
            
            df = pd.read_csv(zip_file.open(file), sep='$', dtype=str)
            print(f"File loaded to pandas {df.shape}")

            spark_df = ss.createDataFrame(df)
            print("Loaded as a Spark DataFrame")

            spark_df = spark_df.withColumn(
                "_hash_id",
                sha2(concat_ws("||", *[col(c) for c in spark_df.columns]), 256)
            )
            
            spark_df = spark_df.withColumn(
                "ingestion_timestamp",
                current_timestamp()
            )
            print("Added metadata columns")

            spark_df.write.format("delta").mode("append").saveAsTable(tb_name)
            print("Loaded to Databricks")
        



if __name__ == "__main__":
    #checkStatus(links["2025_q3"])

    spark = sparkSession()
    print('spark session created')
    readFile(spark, sample_file)
