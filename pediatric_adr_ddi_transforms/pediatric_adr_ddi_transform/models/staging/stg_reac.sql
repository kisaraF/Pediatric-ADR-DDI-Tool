WITH base_reac AS (
    SELECT
        primaryid,
        caseid,
        pt,
        drug_rec_act,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','reac') }}
    QUALIFY
        row_number()
            OVER (PARTITION BY _hash_id ORDER BY ingestion_timestamp DESC)
        = 1
)

SELECT *
FROM base_reac
