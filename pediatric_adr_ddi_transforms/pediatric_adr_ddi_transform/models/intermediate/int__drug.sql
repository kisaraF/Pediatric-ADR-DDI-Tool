{% set pid_list = get_demo_primary_ids() %}

with base as (
  select 
    primaryid, 
    caseid, 
    drug_seq, 
    role_cod, 
    upper(drugname) as drugname, 
    upper(prod_ai) as prod_ai
  from {{ ref('stg_drug') }}
  where drugname is not null
  and primaryid in (
    {% for id in pid_list %}
        '{{ id }}'{% if not loop.last %}, {% endif %}
    {% endfor %}
  )
)
,
lookup_1 as (
  select  
    drugname,
    prod_ai
  from base
  qualify row_number() over (partition by drugname, prod_ai order by prod_ai) = 1
)
,
lookup_counts as (
  select 
    drugname, 
    count(drugname) as drug_count
  from lookup_1
  group by 1
  having drug_count > 1
)
,
filtered_lookup as (
  select 
    *,
    length(prod_ai) as wc_len
  from lookup_1
  where drugname not in (
    select distinct drugname
    from lookup_counts
  )
  and prod_ai is not null
)
,
filtered_lookup_final as (
  select 
    drugname,
    coalesce(prod_ai, 'NA') as prod_ai
  from filtered_lookup
  qualify dense_rank() over(partition by drugname order by wc_len desc) <> 2
)
, 
final as (
    select 
    base.primaryid, 
    base.caseid, 
    base.drug_seq, 
    base.role_cod, 
    flf.drugname, 
    flf.prod_ai
    from base
    left join filtered_lookup_final flf
    on base.drugname = flf.drugname
)

select *
from final