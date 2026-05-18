with base as (
    select
        primaryid,
        caseid,
        i_f_code,
        age::int as age,
        age_cod,
        age_grp,
        sex,
        wt::double,
        wt_cod,
        init_fda_dt,
        init_fda_dt::int as init_fda_dt_int,
        fda_dt,
        reporter_country,
        occr_country
    from {{ ref('stg_demo') }}
    where
        age_grp in ("N", "I", "C", "T")
        or (
            age_grp is null and age < 19
        )
)
,
age_check as (
    select
        *,
        case
            when
                age is not null
                and age_cod is null
                and (age_grp is null or age_grp is not null)
                then true
            when age > 18 and age_cod == "YR" then true
            when age_cod == "DEC" then true
            when age_cod is null and age is null then true
            else false
        end as age_check_i
    from base
    where
        sex is not null
        and sex in ("F", "M")
)
,
age_uniformity as (
    select
        *,
        case
            when age_cod = "MON" then round(age / 12, 2)
            when age_cod = "WK" then round(age / 52.1429, 2)
            when age_cod = "DY" then round(age / 365, 2)
            when age_cod = "HR" then round(age / 8760, 2)
            when age_cod = "YR" then age
            else -1
        end as age_yrs
    from age_check
    where age_check_i = false
)
,
age_binning as (
    select
        *,
        case
            when age_yrs < 0.08 then "Neonate"
            when age_yrs >= 0.08 and age_yrs < 1 then "Infant"
            when age_yrs >= 1 and age_yrs < 4 then "Toddler"
            when age_yrs >= 4 and age_yrs < 7 then "Preschooler"
            when age_yrs >= 7 and age_yrs < 13 then "Child"
            when age_yrs >= 13 and age_yrs < 19 then "Teenager"
            else "NA_VAL"
        end as age_bin
    from age_uniformity
    where age_yrs > 0
)
,
get_origin_country as (
    select
        *,
        case
            when
                reporter_country = "COUNTRY NOT SPECIFIED"
                and occr_country is not null
                then occr_country
            when
                reporter_country <> "COUNTRY NOT SPECIFIED"
                and occr_country is not null
                then occr_country
            when
                reporter_country = "COUNTRY NOT SPECIFIED"
                and occr_country is null
                then "COUNTRY NOT SPECIFIED"
            when
                reporter_country <> "COUNTRY NOT SPECIFIED"
                and occr_country is null
                then reporter_country
        end as origin_country
    from age_binning
)
,
conv_lbs_to_kg as (
    select
        *,
        case
            when wt_cod is not null and wt_cod = "LBS" then round(wt / 2.2, 2)
            when wt_cod is not null and wt_cod = "KG" then round(wt / 2.2, 2)
        end as wt_kg,
        coalesce(wt is not null and wt_cod is null, false) as wt_check
    from get_origin_country
    where origin_country <> "COUNTRY NOT SPECIFIED"
)
,
weight_outliers as (
    select
        *,
        case
            when wt_kg is null then "Missing weight"
            when
                age_bin = "Neonate" and (wt_kg >= 2.5 and wt_kg < 4.5)
                then "Valid Weight"
            when
                age_bin = "Infant" and (wt_kg >= 4.4 and wt_kg < 11.3)
                then "Valid Weight"
            when
                age_bin = "Toddler" and (wt_kg >= 8.5 and wt_kg < 17.5)
                then "Valid Weight"
            when
                age_bin = "Preschooler" and (wt_kg >= 12.5 and wt_kg < 25.8)
                then "Valid Weight"
            when
                age_bin = "Child" and (wt_kg >= 19.8 and wt_kg < 51)
                then "Valid Weight"
            when
                age_bin = "Teenager" and (wt_kg >= 39 and wt_kg < 81)
                then "Valid Weight"
            else "Invalid Weight"
        end as outlier_check
    from conv_lbs_to_kg
    where wt_check is not true
)
,
final as (
    select
        primaryid,
        caseid,
        i_f_code,
        age_yrs,
        age_bin,
        sex,
        wt_kg,
        origin_country,
        init_fda_dt,
        fda_dt
    from weight_outliers
    where
        outlier_check <> "Invalid Weight"
        and age_yrs > 0
        and init_fda_dt_int >= 20210101
        and origin_country = "US" -- make sure only US caes are taken
)

select *
from final
