{{ config(tags=["marts", "dispropotionality_ratios"], materialized="view") }}

with base as (
    select
        *,
        case
            when
                contingency_a + contingency_b is not null
                then contingency_a + contingency_b
            when contingency_a + contingency_b is null then null
        end as prr_ab_d,
        case
            when
                contingency_c + contingency_d is not null
                then contingency_c + contingency_d
            when contingency_c + contingency_d is null then null
        end as prr_cd_d
    from {{ ref('contingency_table') }}
)
,
dr_compute as (
    select
        *,
        try_divide((contingency_a / prr_ab_d), (contingency_c / prr_cd_d))
            as prr,
        try_divide(
            (contingency_a * contingency_d), (contingency_b * contingency_c)
        ) as ror
    from base
)
,
dr_ci_anchor as (
    select
        *,
        sqrt(
            (1 / contingency_a)
            - (1 / prr_ab_d)
            + (1 / contingency_c)
            - (1 / prr_cd_d)
        ) as se_prr,
        sqrt(
            (1 / contingency_a)
            + (1 / contingency_b)
            + (1 / contingency_c)
            + (1 / contingency_d)
        ) as se_ror
    from dr_compute
)
,
dr_calc_final as (
    select
        *,
        exp(ln(prr) - 1.96 * se_prr) as ci_prr_lower,
        exp(ln(prr) + 1.96 * se_prr) as ci_prr_upper,
        exp(ln(ror) - 1.96 * se_ror) as ci_ror_lower,
        exp(ln(ror) + 1.96 * se_ror) as ci_ror_upper
    from dr_ci_anchor
)

select *
from dr_calc_final
