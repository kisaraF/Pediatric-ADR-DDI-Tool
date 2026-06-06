with base as (
	select
		primaryid, 
		explode(filter(adr_case, x -> x like 'drug_%')) as drug,
		explode(filter(adr_case, x -> x like 'reaction_%')) as reaction
	from pediatric_adr_events.dbt_transforms_arm_data.arm__transactions
)
,
Total_Count as ( 
	select count(distinct primaryid) as total_N
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
	select base.*, d.drug_count, r.reaction_count, tot.N_, t.total_N
	from base
	left join Drug_count d 
	on d.drug = base.drug
	left join Reaction_count r 
	on r.reaction = base.reaction
	left join N_count tot
	on tot.reaction = base.reaction 
	and tot.drug = base.drug
	cross join Total_Count t
)

select distinct h.* 
from (
	select 
		* except(primaryid),
		round((drug_count * reaction_count) / total_N,2) as E_
	from combined_base
) h