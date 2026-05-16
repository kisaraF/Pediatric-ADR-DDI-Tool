import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from fetch_drug_match import get_drug_match
from itertools import batched
from pediatric_adr_shared.logging_mod import init_logger

logger = init_logger()
src_table = "pediatric_adr_events.raw_source.drug"
tgt_table = "pediatric_adr_events.raw_source.rxnorm_key"


def get_spark() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def write_results(spark: SparkSession, tgt_table_name: str, itm_ls: list[str]):
    results = [get_drug_match(drug) for drug in itm_ls]
    results_df = spark.createDataFrame(results)
    results_df = results_df.select(
        "drug_raw",
        "match_rxcui",
        "match_rank",
        "match_name",
        "match_source",
        "bn_rxcui",
        "bn_name",
        "in_rxcui",
        "in_name",
    )
    results_df = results_df.withColumn("added_datetime", current_timestamp())

    # append to the target table
    results_df.writeTo(tgt_table_name).append()
    logger.info("Result set appended to the target table")


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
FROM {raw_table_name} as raw
LEFT JOIN {tgt_table_name} as tgt
ON tgt.drug_raw = raw.drugname
WHERE tgt.drug_raw IS NULL
"""

    df = spark.sql(query).limit(20)
    # convert the drugs to a list
    drugs_list = [row["drugname"] for row in df.select("drugname").collect()]
    # break into chunks if there are too much
    if len(drugs_list) > 10:
        logger.info(
            f"Drugs list has more than {len(drugs_list)} items. Hence, using chunks of 10"
        )
        for chunk in batched(drugs_list, 10):
            write_results(spark, tgt_table_name, chunk)
    else:
        write_results(spark, tgt_table_name, drugs_list)


if __name__ == "__main__":
    get_drugs_list(src_table, tgt_table)
