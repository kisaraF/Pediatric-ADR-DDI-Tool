WITH base_drug AS (
    SELECT
        primaryid,
        caseid,
        drug_seq,
        role_cod,
        drugname,
        prod_ai,
        val_vbm,
        route,
        dose_vbm,
        cum_dose_chr,
        cum_dose_unit,
        dechal,
        rechal,
        lot_num,
        exp_dt,
        nda_num,
        dose_amt,
        dose_unit,
        dose_form,
        dose_freq,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','drug') }}
    QUALIFY
        row_number()
            OVER (PARTITION BY _hash_id ORDER BY ingestion_timestamp DESC)
        = 1
)

SELECT *
FROM base_drug
