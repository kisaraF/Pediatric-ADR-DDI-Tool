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
-- Use RxNorm table and join it's info
rx_norm as (
    select distinct upper(drug_raw) as drug_name, in_name
    from {{ source('raw', 'rxnorm_key') }}
    where drug_raw <> "dummy"
)

select base.*, rx_norm.in_name as rxnorm_in
from base
left join rx_norm
on base.drugname = rx_norm.drug_name