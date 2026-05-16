import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from fetch_drug_match import get_drug_match


def get_spark() -> SparkSession:
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):  # for DAB jobs
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession  # else local development

    return DatabricksSession.builder.getOrCreate()


def get_drugs_list(
    spark: SparkSession, raw_table_name: str, tgt_table_name: str
) -> list:
    """
    Get each drug and their related info from RxNorm API.
    Uses a UDF to pass each drug name to fetch custom function
    and assume a struct data type to the return dictionary
    and extend the dataframe to have result values
    """
    # only consider that are already not in the base
    query = f"""
SELECT DISTINCT raw.drugname
FROM {raw_table_name} as raw
LEFT JOIN {tgt_table_name} as tgt
ON tgt.drug_raw = raw.drugname
WHERE tgt.drug_raw IS NULL
"""

    df = spark.sql(query).limit(3)
    # convert the drugs to a list
    drugs_list = [row["drugname"] for row in df.select("drugname").collect()]
    results = [get_drug_match(drug) for drug in drugs_list]
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


if __name__ == "__main__":
    ss = get_spark()
    src_table = "pediatric_adr_events.raw_source.drug"
    tgt_table = "pediatric_adr_events.raw_source.rxnorm_key"
    get_drugs_list(ss, src_table, tgt_table)
