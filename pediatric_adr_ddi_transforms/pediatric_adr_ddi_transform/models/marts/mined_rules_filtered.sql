{{ config(tags=["marts", "rules_mined_filtered"]) }}

with base_filtering as (
    select
        *,
        size(filter(antecedent, z -> z ilike 'reac_%')) as reac_count
    from {{ source('mined_rules_db', 'mined_rules') }}
    where
        exists(antecedent, x -> x ilike 'drug_%')
        and exists(antecedent, x -> x ilike 'demo_age_%')
        and exists(antecedent, x -> x ilike 'demo_sex_%')
        and exists(antecedent, x -> x ilike 'demo_weight_%')
        and not exists(antecedent, x -> x ilike 'outc_%')
        and not exists(consequent, y -> y ilike 'outc_%')
)

select 
    *,
    sha2(concat_ws('||', *),256) id_col
from base_filtering
where confidence < 1
order by lift desc, reac_count desc
