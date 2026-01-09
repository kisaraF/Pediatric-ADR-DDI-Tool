WITH base_demo AS (
    select 
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
    from {{ source('raw','demo') }}
    qualify row_number() over(partition by _hash_id order by ingestion_timestamp desc) = 1
)

SELECT *
FROM base_demo