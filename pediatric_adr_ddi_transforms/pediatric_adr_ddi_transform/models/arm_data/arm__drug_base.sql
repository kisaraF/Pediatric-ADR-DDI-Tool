with drug_base as (
  select 
    *,
    'drug_' || {{ clean_string('drugname') }} as drugname_clean
  from {{ ref('int__drug') }}
)
,
cleaned_drugs as (
  select 
    primaryid,
    drugname_clean as drugname
  from drug_base
  qualify row_number() over(partition by primaryid, drugname_clean order by primaryid) = 1
)
,
final as (
  select 
    primaryid,
    array_join(collect_set(drugname), ', ') AS drugs
  from cleaned_drugs
  group by primaryid
)

select *
from final