WITH base_demo AS (
    SELECT
        primaryid,
        caseid,
        caseversion,
        i_f_code,
        event_dt,
        mfr_dt,
        init_fda_dt,
        fda_dt,
        rept_cod,
        auth_num,
        mfr_num,
        mfr_sndr,
        lit_ref,
        age,
        age_cod,
        age_grp,
        sex,
        e_sub,
        wt,
        wt_cod,
        rept_dt,
        to_mfr,
        occp_cod,
        reporter_country,
        occr_country,
        _hash_id,
        ingestion_timestamp
    FROM {{ source('raw','demo') }}
    QUALIFY
        row_number()
            OVER (PARTITION BY _hash_id ORDER BY ingestion_timestamp DESC)
        = 1
)

SELECT *
FROM base_demo
