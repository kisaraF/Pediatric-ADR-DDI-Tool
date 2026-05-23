{{ config(tags=["intermediate", "rnxnorm"]) }}

with us_drug_cases as (
    select distinct
        primaryid,
        drugname
    from pediatric_adr_events.raw_source.drug
    where primaryid in (
        select distinct primaryid
        from {{ ref('stg_demo') }}
    )
)
,
drug_raw as (
    select
        trim(regexp_replace(lower(drugname), '[\\[\\]]', '')) as drug_n,
        trim(regexp_replace(lower(prod_ai), '[\\[\\]]', '')) as prod_ai
    from {{ ref('stg_drug') }}
)
,
rxnorm_clean as (
    select distinct
        match_rank,
        match_score,
        match_source,
        trim(regexp_replace(lower(drug_raw), '[\\[\\]]', '')) as drug_raw,
        trim(regexp_replace(lower(in_name), '[\\[\\]]', '')) as in_name
    from {{ source('raw', 'rxnorm_key') }}
)
,
rxnorm_base as (
    select distinct
        rk.drug_raw,
        rk.in_name,
        dr.prod_ai,
        rk.match_rank,
        rk.match_score,
        rk.match_source
    from rxnorm_clean as rk
    left join drug_raw as dr
        on rk.drug_raw = dr.drug_n
)
,
approximates as (
    select
        *,
        levenshtein(drug_raw, in_name) as levenstein_score_p,
        greatest(length(drug_raw), length(in_name)) as max_len_drug_p,
        levenshtein(prod_ai, in_name) as levenstein_score_s,
        greatest(length(prod_ai), length(in_name)) as max_len_drug_s,
        -- tokenize ingredient name
        case
            when contains(in_name, 'vitamin') then array(in_name)
            when contains(in_name, '/') then split(in_name, '/')
            when contains(in_name, ',') then split(in_name, ',')
            else split(in_name, ' ')
        end as ingredient_tokens,
        case
            when contains(drug_raw, 'vitamin') then array(drug_raw)
            when contains(drug_raw, '/') then split(drug_raw, '/')
            when contains(drug_raw, ',') then split(drug_raw, ',')
            else split(drug_raw, ' ')
        end as drug_tokens,
        case
            when contains(prod_ai, 'vitamin') then array(prod_ai)
            when contains(prod_ai, '/') then split(prod_ai, '/')
            when contains(prod_ai, ',') then split(prod_ai, ',')
            else split(prod_ai, ' ')
        end as prod_ai_tokens,
        soundex(drug_raw) as soundex_drug,
        soundex(in_name) as soundex_in,
        soundex(prod_ai) as soundex_prod_ai
    from rxnorm_base
    where
        match_rank <> 100
        and match_rank is not null
)
,
approximates_transformed as (
    select
        *,
        round(1 - (levenstein_score_p / max_len_drug_p), 2) as nls_p,
        round(1 - (levenstein_score_s / max_len_drug_s), 2) as nls_s,
        size(array_intersect(ingredient_tokens, drug_tokens))
        / least(size(ingredient_tokens), size(drug_tokens))
            as token_overlap_score_p,
        size(array_intersect(ingredient_tokens, prod_ai_tokens))
        / least(size(ingredient_tokens), size(prod_ai_tokens))
            as token_overlap_score_s,
        case when soundex_drug = soundex_in then 1 end as sm_dr_in,
        case when soundex_in = soundex_prod_ai then 1 end as sm_pa_in
    from approximates
)
,
approximates_matching as (
    select
        drug_raw,
        in_name,
        sha2(concat(drug_raw, in_name), 256) as id_
    from approximates_transformed
    where
        nls_p >= 0.9
        or token_overlap_score_p >= 0.8
        or sm_dr_in = 1
        or nls_s >= 0.9
        or token_overlap_score_s >= 0.8
        or sm_pa_in = 1
),

rx_norm_base as (
    select
        * except (drug_raw),
        trim(regexp_replace(lower(drug_raw), '[\\[\\]]', '')) as drug_raw,
        sha2(
            concat(
                trim(regexp_replace(lower(drug_raw), '[\\[\\]]', '')),
                trim(regexp_replace(lower(in_name), '[\\[\\]]', ''))
            ),
            256
        ) as id_
    from pediatric_adr_events.raw_source.rxnorm_key
)
,
final_rxnorm as (
    select *
    from rx_norm_base
    where match_rank = 100
    union distinct
    select *
    from rx_norm_base
    where match_score is null
    union distinct
    select rnc.*
    from rx_norm_base as rnc
    inner join approximates_matching as am
        on rnc.id_ = am.id_
)

select *
from final_rxnorm
where drug_raw <> 'dummy'
