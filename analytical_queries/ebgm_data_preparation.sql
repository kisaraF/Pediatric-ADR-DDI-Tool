with base as (
	select
		primaryid, 
		explode(filter(adr_case, x -> x like 'drug_%')) as drug,
		explode(filter(adr_case, x -> x like 'reaction_%')) as reaction
	from pediatric_adr_events.dbt_transforms_arm_data.arm__transactions
)
,
N_count as (
	select drug, reaction, count(distinct primaryid) as N_
	from base
	group by drug, reaction
)
,
Drug_count as (
	select drug, count(distinct primaryid) as drug_count
	from base
	group by drug
)
,
Reaction_count as (
	select reaction, count(distinct primaryid) as reaction_count
	from base
	group by reaction
)
,
combined_base as (
	select base.*, d.drug_count, r.reaction_count, tot.N_
	from base
	left join Drug_count d 
	on d.drug = base.drug
	left join Reaction_count r 
	on r.reaction = base.reaction
	left join N_count tot
	on tot.reaction = base.reaction 
	and tot.drug = base.drug
)

select 
	*,
	round((drug_count * reaction_count) / N_,2) as E_
from combined_base