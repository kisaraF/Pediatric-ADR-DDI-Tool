{{ config(tags=['marts', 'disprop_report'], materialized='view') }}

with qualified_items as (
    select
        id_col,
        drug_item,
        reaction,
        prr,
        ror,
        ci_prr_lower,
        ci_ror_lower,
        contingency_a
    from {{ ref('disprop_ratios') }}
    where
        prr >= 2
        and ci_prr_lower > 1
        and ror >= 2
        and ci_ror_lower > 1
        and contingency_a >= 3
)

select
    r.* except (id_col),
    qi.* except (id_col),
    r.id_col
from (
    select *
    from {{ ref('mined_rules_filtered') }}
    where id_col in (
        select distinct id_col
        from {{ ref('contingency_table') }}
    )
) as r
inner join qualified_items as qi
    on r.id_col = qi.id_col
order by id_col asc, prr desc
