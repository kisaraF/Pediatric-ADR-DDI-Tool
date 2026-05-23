from databricks.connect import DatabricksSession
import joblib
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

model1 = joblib.load(
    "/Workspace/Users/kisarawenu@gmail.com/Pediatric ADR DDI Tool/prediction_models/rf_age_grp_1.pkl"
)
model2 = joblib.load(
    "/Workspace/Users/kisarawenu@gmail.com/Pediatric ADR DDI Tool/prediction_models/rf_age_grp_2.pkl"
)
model3 = joblib.load(
    "/Workspace/Users/kisarawenu@gmail.com/Pediatric ADR DDI Tool/prediction_models/rf_age_grp_3.pkl"
)


@F.pandas_udf(DoubleType())
def predict_grp1(
    age_norm: pd.Series, age_bin: pd.Series, gen: pd.Series, coun: pd.Series
) -> pd.Series:
    X = pd.DataFrame(
        {
            "age_norm": age_norm,
            "age_bin_enc": age_bin,
            "gender_enc": gen,
            "origin_country_enc": coun,
        }
    )
    return pd.Series(model1.predict(X))


@F.pandas_udf(DoubleType())
def predict_grp2(
    age_norm: pd.Series, age_bin: pd.Series, gen: pd.Series, coun: pd.Series
) -> pd.Series:
    X = pd.DataFrame(
        {
            "age_norm": age_norm,
            "age_bin_enc": age_bin,
            "gender_enc": gen,
            "origin_country_enc": coun,
        }
    )
    return pd.Series(model2.predict(X))


@F.pandas_udf(DoubleType())
def predict_grp3(
    age_norm: pd.Series, age_bin: pd.Series, gen: pd.Series, coun: pd.Series
) -> pd.Series:
    X = pd.DataFrame(
        {
            "age_norm": age_norm,
            "age_bin_enc": age_bin,
            "gender_enc": gen,
            "origin_country_enc": coun,
        }
    )
    return pd.Series(model3.predict(X))


def main():
    # Read the feature encoded table to a DF and split for predicting
    df = spark.read.table(
        "pediatric_adr_events.dbt_transforms_intermediate.int__demo_feature_encoded"
    )
    df_complete = df.filter(F.col("wt_kg").isNotNull())
    df_missing = df.filter(F.col("wt_kg").isNull())

    # Apply predictions based on age_bin_enc
    # Group 1: Teens & Child (4, 5)
    preds_1 = df_missing.filter(F.col("age_bin_enc").isin([4, 5])).withColumn(
        "wt_kg",
        predict_grp1("age_norm", "age_bin_enc", "gender_enc", "origin_country_enc"),
    )

    # Group 2: Preschooler & Toddler (2, 3)
    preds_2 = df_missing.filter(F.col("age_bin_enc").isin([2, 3])).withColumn(
        "wt_kg",
        predict_grp2("age_norm", "age_bin_enc", "gender_enc", "origin_country_enc"),
    )

    # Group 3: Neonates & Infants (0, 1)
    preds_3 = df_missing.filter(F.col("age_bin_enc").isin([0, 1])).withColumn(
        "wt_kg",
        predict_grp3("age_norm", "age_bin_enc", "gender_enc", "origin_country_enc"),
    )

    # 4. FINAL UNION
    # Combine the original weights with the newly predicted weights
    final_df = (
        df_complete.unionByName(preds_1).unionByName(preds_2).unionByName(preds_3)
    )

    final_df = final_df.withColumn("wt_kg", F.round(F.col("wt_kg"), 2))

    cols_to_select = [
        "primaryid",
        "caseid",
        "i_f_code",
        "age_yrs",
        "age_bin",
        "sex",
        "origin_country",
        "wt_kg",
        "init_fda_dt",
        "fda_dt",
    ]

    final_df = final_df.select(*cols_to_select)

    # Write to a delta table
    final_df.write.mode("overwrite").format("delta").saveAsTable(
        "pediatric_adr_events.nb_transforms_intermediate.int__demo_complete"
    )


if __name__ == "__main__":
    # Getting a spark session
    spark = DatabricksSession.builder.serverless().profile("DEFAULT").getOrCreate()
    main()
