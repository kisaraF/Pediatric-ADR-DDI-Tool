{{ config(tags=["staging", "outc"]) }}

WITH base_outc AS (
    SELECT
        primaryid,
        caseid,
        outc_cod,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','outc') }}
    QUALIFY
        row_number()
            OVER (PARTITION BY _hash_id ORDER BY ingestion_timestamp DESC)
        = 1
)

SELECT *
FROM base_outc
