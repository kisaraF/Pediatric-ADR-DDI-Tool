{{ config(tags=["arm_data", "outc_base"]) }}

with outc_base as (
  select 
    *,
    'outc_' || {{ clean_string('outc_cod') }} as outc_clean
  from {{ ref('int__outc') }}
)
,
cleaned_outc as (
  select 
    primaryid,
    outc_clean as outcome
  from outc_base
  qualify row_number() over(partition by primaryid, outc_clean order by primaryid) = 1
)
,
final as (
  select 
    primaryid,
    array_join(collect_set(outcome), ', ') AS outcomes
  from cleaned_outc
  group by primaryid
)

select *
from final