with reac_base as (
  select 
    *,
    'reaction_' || {{ clean_string('pt') }} as pt_clean
  from {{ ref('int__reac') }}
)
,
cleaned_reac as (
  select 
    primaryid,
    pt_clean as reaction
  from reac_base
  qualify row_number() over(partition by primaryid, pt_clean order by primaryid) = 1
)
,
final as (
  select 
    primaryid,
    array_join(collect_set(reaction), ', ') AS reactions
  from cleaned_reac
  group by primaryid
)

select *
from final