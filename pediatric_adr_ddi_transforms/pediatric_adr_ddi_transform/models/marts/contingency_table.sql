{{ config(tags=["marts", "contingency_matrix"]) }}

with
rules_base as (
    select
        id_col,--should be addeded to marts table
        filter(antecedent, x -> x ilike 'drug_%') as drugs,
        consequent[0] as reaction,
        size(drugs) as drug_count
    from {{ ref('mined_rules_filtered') }}
)
,
exclude_unwanted_reactions as (
    select *
    from rules_base
    where reaction not in (
        select distinct unwanted_reactions
        from {{ ref('unwanted_reactions') }}
    )
)
,
items_filtered as (
    select *
    from exclude_unwanted_reactions
    qualify -- removing duplicates. some rules have the same stuff
        row_number() over (partition by drugs, reaction order by drug_count) = 1
)
,
items_exploded as (
    select
        id_col,
        reaction,
        explode(drugs) as drug_item
    from items_filtered
)
,
total_cases as (
    -- Get the total number of transactions in the database (A + B + C + D)
    select count(distinct primaryid) as total_n
    from {{ ref('arm__transactions') }}
),

exploded_transactions as (
    -- Explode transactions once to get case-level drug/reaction pairs
    select
        primaryid,
        explode(filter(adr_case, x -> x ilike 'drug_%')) as drug,
        explode(filter(adr_case, y -> y ilike 'reac_%')) as reaction
    from {{ ref('arm__transactions') }}
),

pair_counts as (
    -- Count A: Drug + Reaction together
    select
        drug,
        reaction,
        count(distinct primaryid) as count_a
    from exploded_transactions
    group by drug, reaction
),

drug_counts as (
    -- Count Total Drug (A + B)
    select
        drug,
        count(distinct primaryid) as count_drug_total
    from exploded_transactions
    group by drug
),

reaction_counts as (
    -- Count Total Reaction (A + C)
    select
        reaction,
        count(distinct primaryid) as count_reaction_total
    from exploded_transactions
    group by reaction
)

-- Now join these pre-calculated aggregates to your target rules
select
    r.id_col,
    r.drug_item,
    r.reaction,
    coalesce(pc.count_a, 0) as contingency_a,
    coalesce(dc.count_drug_total, 0) - coalesce(pc.count_a, 0) as contingency_b,
    coalesce(rc.count_reaction_total, 0)
    - coalesce(pc.count_a, 0) as contingency_c,
    (select total_n from total_cases)
    - coalesce(dc.count_drug_total, 0)
    - coalesce(rc.count_reaction_total, 0)
    + coalesce(pc.count_a, 0) as contingency_d
from items_exploded as r
left join pair_counts as pc
    on r.drug_item = pc.drug and r.reaction = pc.reaction
left join drug_counts as dc
    on r.drug_item = dc.drug
left join reaction_counts as rc
    on r.reaction = rc.reaction
