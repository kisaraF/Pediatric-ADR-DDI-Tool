import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, FloatType
from fetch_drug_match import get_drug_match
from itertools import batched
from pediatric_adr_shared.logging_mod import init_logger
from concurrent.futures import ThreadPoolExecutor

logger = init_logger()
src_table = "pediatric_adr_events.raw_source.drug"
tgt_table = "pediatric_adr_events.raw_source.rxnorm_key"


def get_spark() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def write_results(spark: SparkSession, tgt_table_name: str, itm_ls: list[str]):
    schema_i = StructType(
        [
            StructField("drug_raw", StringType(), nullable=True),
            StructField("match_rxcui", LongType(), nullable=True),
            StructField("match_rank", LongType(), nullable=True),
            StructField("match_score", FloatType(), nullable=True),
            StructField("match_name", StringType(), nullable=True),
            StructField("match_source", StringType(), nullable=True),
            StructField("bn_rxcui", LongType(), nullable=True),
            StructField("bn_name", StringType(), nullable=True),
            StructField("in_rxcui", LongType(), nullable=True),
            StructField("in_name", StringType(), nullable=True),
        ]
    )
    results = []
    with ThreadPoolExecutor(max_workers=20) as worker:
        result_sub = list(worker.map(get_drug_match, itm_ls))
    for sub in result_sub:
        if isinstance(sub, list):
            for i in sub:
                results.append(i)
        else:
            results.append(sub)
    results_df = spark.createDataFrame(results, schema=schema_i)
    results_df = results_df.select(
        "drug_raw",
        "match_rxcui",
        "match_rank",
        "match_score",
        "match_name",
        "match_source",
        "bn_rxcui",
        "bn_name",
        "in_rxcui",
        "in_name",
    )
    results_df = results_df.withColumn("added_datetime", current_timestamp())
    logger.info("Adding timestamp auditing column")
    # append to the target table
    results_df.writeTo(tgt_table_name).append()
    logger.info("Result set appended to the target table\n\n")


def get_drugs_list(
    raw_table_name: str = src_table, tgt_table_name: str = tgt_table
) -> list:
    """
    Get each drug and their related info from RxNorm API.
    Uses a UDF to pass each drug name to fetch custom function
    and assume a struct data type to the return dictionary
    and extend the dataframe to have result values
    """
    spark = get_spark()
    # only consider that are already not in the base
    query = f"""
SELECT DISTINCT raw.drugname
FROM (
    SELECT upper(drugname) as drugname
    FROM {raw_table_name}
    WHERE primaryid IN (
        SELECT DISTINCT primaryid
        FROM pediatric_adr_events.raw_source.demo
        WHERE occr_country = 'US' 
        OR reporter_country = 'US'
    )
    AND drugname IS NOT NULL
) as raw
LEFT JOIN (
    SELECT upper(drug_raw) as drug_raw
    FROM {tgt_table_name}
) as tgt
ON tgt.drug_raw = raw.drugname
WHERE tgt.drug_raw IS NULL
"""

    df = spark.sql(query)
    # convert the drugs to a list
    drugs_list = [row["drugname"] for row in df.select("drugname").collect()]
    logger.info(f"Identified {len(drugs_list)} drugs to be RxNorm normalization\n")
    # break into chunks if there are too much
    chunk_size = 40
    if len(drugs_list) > chunk_size:
        logger.info(
            f"Drugs list has more than {len(drugs_list)} items. Hence, using chunks of {chunk_size}"
        )
        for chunk in batched(drugs_list, chunk_size):
            write_results(spark, tgt_table_name, chunk)
    else:
        write_results(spark, tgt_table_name, drugs_list)


if __name__ == "__main__":
    get_drugs_list(src_table, tgt_table)
