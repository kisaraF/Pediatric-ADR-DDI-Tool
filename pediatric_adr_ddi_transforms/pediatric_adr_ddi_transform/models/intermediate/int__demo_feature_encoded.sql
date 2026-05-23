{{ config(tags=["intermediate", "demo_feature_encoding"]) }}

with base as (
    select
        *,
        min(age_yrs) over (order by age_yrs) as min_age,
        max(age_yrs) over (order by age_yrs desc) as max_age
    from {{ ref('int__demo_base') }}
)
,
country_list as (
    select distinct origin_country
    from base
)
,
country_lookup as (
    select
        origin_country,
        rank() over (order by origin_country) as country_rank
    from country_list
)
,
encoding_attributes as (
    select
        base.*,
        cl.country_rank as origin_country_enc,
        case
            when base.sex = "M" then 0
            when base.sex = "F" then 1
        end as gender_enc,
        case
            when base.age_bin = "Neonate" then 0
            when base.age_bin = "Infant" then 1
            when base.age_bin = "Toddler" then 2
            when base.age_bin = "Preschooler" then 3
            when base.age_bin = "Child" then 4
            when base.age_bin = "Teenager" then 5
        end as age_bin_enc,
        (age_yrs - min_age) / (max_age - min_age) as age_norm
    from base
    left join country_lookup as cl
        on base.origin_country = cl.origin_country
)
,
final as (
    select
        primaryid,
        caseid,
        i_f_code,
        age_yrs,
        age_bin,
        age_norm,
        age_bin_enc,
        sex,
        wt_kg,
        gender_enc,
        origin_country,
        origin_country_enc,
        init_fda_dt,
        fda_dt
    from encoding_attributes
)

select *
from final
