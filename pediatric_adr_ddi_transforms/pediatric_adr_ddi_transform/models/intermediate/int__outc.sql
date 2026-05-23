{{ config(tags=["intermediate", "outcomes"]) }}

{% set pid_list = get_demo_primary_ids() %}

with base as (
  select 
    *
  from {{ ref('stg_outc') }}
  where primaryid in (
    {% for id in pid_list %}
        '{{ id }}'{% if not loop.last %}, {% endif %}
    {% endfor %}
  )
)

select *
from base