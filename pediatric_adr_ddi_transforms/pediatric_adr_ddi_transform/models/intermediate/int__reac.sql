{% set pid_list = get_demo_primary_ids() %}

with base as (
  select 
    primaryid, 
    caseid, 
    pt
  from {{ ref('stg_reac') }}
  where primaryid in (
    {% for id in pid_list %}
        '{{ id }}'{% if not loop.last %}, {% endif %}
    {% endfor %}
  )
)

select *
from base