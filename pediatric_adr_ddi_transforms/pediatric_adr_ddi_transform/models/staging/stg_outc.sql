WITH base_outc AS (
    SELECT 
        primaryid,
        caseid,
        outc_cod,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','outc') }}
    qualify row_number() over(partition by _hash_id order by ingestion_timestamp desc) = 1
)

SELECT *
FROM base_outc