{{ config(tags=["arm_data", "demo_base"]) }}

with demo_base as (
    select
        primaryid,
        lower(age_bin) as age_bin,
        case
            when wt_kg < 5 then lower('Bellow 5 kg')
            when wt_kg < 10 then lower('5-10 kg')
            when wt_kg < 20 then lower('10-20 kg')
            when wt_kg < 40 then lower('20-40 kg')
            when wt_kg < 60 then lower('40-60 kg')
            else lower('Above 60 kg')
        end as wt_bin,
        lower(sex) as sex
        -- lower(origin_country) as origin_country
    from {{ source('clean_demo','int__demo_complete') }}
    qualify
        row_number()
            over (
                partition by primaryid, age_bin, wt_bin, sex --, origin_country
                order by primaryid
            )
        = 1
)
,
final as (
    select
        primaryid,
        'demo_age_bin_' || age_bin as age_bin_re,
        'demo_weight_' || wt_bin as wt_bin_re,
        'demo_sex_' || sex as sex_re
        -- No need to have origin_country as of now since it's strictly USA based
        -- 'demo_origin_' || origin_country as origin_country_re
    from demo_base
)

select *
from final
