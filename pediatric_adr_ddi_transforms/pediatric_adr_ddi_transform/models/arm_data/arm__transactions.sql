{{ config(tags=["arm_data", "transactions"]) }}

with base as (
    select
        demo.primaryid,
        demo.age_bin_re as age_bin,
        demo.wt_bin_re as wt_bin,
        demo.sex_re,
        -- demo.origin_country_re as origin_country,
        drug.drugs,
        reac.reactions,
        outc.outcomes
    from {{ ref('arm__demo_base') }} as demo
    left join {{ ref('arm__reac_base') }} as reac
        on demo.primaryid = reac.primaryid
    left join {{ ref('arm__outc_base') }} as outc
        on demo.primaryid = outc.primaryid
    left join {{ ref('arm__drug_base') }}drug
        on demo.primaryid = drug.primaryid
)
,
final as (
    select
        primaryid,
        -- array_distinct ensures no duplicate items in one basket
        -- array_compact (or array_remove) cleans up any NULLs from missing outcomes
        array_distinct(
            array_compact(
                flatten(
                    array(
                        -- Wrap single items in an array so they can be flattened
                        array(age_bin),
                        array(wt_bin),
                        array(sex_re),
                        -- array(origin_country),
                        -- Split existing strings back into arrays
                        split(drugs, ', '),
                        split(reactions, ', '),
                        coalesce(split(outcomes, ', '), array())
                    )
                )
            )
        ) as adr_case
    from base
)

select *
from final
