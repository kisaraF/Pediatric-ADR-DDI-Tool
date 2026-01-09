WITH base_reac AS (
    SELECT 
        primaryid,
        caseid,
        pt,
        drug_rec_act,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','reac') }}
    qualify row_number() over(partition by _hash_id order by ingestion_timestamp desc) = 1
)

SELECT *
FROM base_reac