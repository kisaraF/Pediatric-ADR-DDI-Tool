-- ANALYSIS: 
-- The purpose is to identify how many unique ADR cases are being covered from exact and approximate matches (that passed rules)
--1. Sample data ingestion time period 				=	2026/05/17 to 2026/05/18
--2. Total data (unique) points 					=	20,269 | 20,312 (total)
--3. Ingredient collapsed							= 	Collapsed to 4,447 | no nulls anywhere 
--4. Exact match count 								= 	5583 (unq), 5626 (total)
--5. Exact match % 									=	27.48%
--6. Approximates with rule validation count 		=	6260
--7. Approximate match % 							=	30.81%
--8. Total no matches all & %						=	905 (0.05%)
--9. Total matches 									= 	11886
--10. Total match % 								=	58.51%
--11. Total unique ADR cases (US)					=	1,230,933
--12. How many cases are covered in matches 		= 	1,153,139
--13. %  of cases covered 							=	93.68%

-- 1
select max(added_datetime), min(added_datetime)
from pediatric_adr_events.raw_source.rxnorm_key;

-- 2 & 3
select 
	count(*) total_ , 
	count(distinct drug_raw) unq_total_ ,
	count(distinct in_name) unq_in_total_,
	sum(case when in_name is null then 1 else 0 end) null_in_count
from pediatric_adr_events.raw_source.rxnorm_key
where drug_raw <> 'dummy';

-- 4. 
select count(*), count(distinct drug_raw)
from pediatric_adr_events.raw_source.rxnorm_key
where match_score >= 100
and drug_raw <> 'dummy';

-- 8.
select count(*), count(distinct drug_raw), count(distinct in_name)
from pediatric_adr_events.raw_source.rxnorm_key
where match_rank is null;

-- 6 & 7
with 
drug_raw as (
	select 
		trim(regexp_replace(lower(drugname),'[\\[\\]]', '')) as drug_n,
		trim(regexp_replace(lower(prod_ai),'[\\[\\]]', '')) as prod_ai
	from pediatric_adr_events.raw_source.drug
)
,
rxnorm_clean as (
	select distinct 
		trim(regexp_replace(lower(drug_raw), '[\\[\\]]', '')) as drug_raw,	
		trim(regexp_replace(lower(in_name), '[\\[\\]]', '')) as in_name,
		match_rank,
		match_score,
		match_source
	from pediatric_adr_events.raw_source.rxnorm_key
	where added_datetime like '2026-05-18%' -- sampling for now
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
	from rxnorm_clean rk
	left join drug_raw dr
	on dr.drug_n = rk.drug_raw
)
,
approximates as(
	select 
		*, 
		LEVENSHTEIN(drug_raw, in_name) as levenstein_score_p, 
		greatest(length(drug_raw), length(in_name)) as max_len_drug_p,
		LEVENSHTEIN(prod_ai, in_name) as levenstein_score_s, 
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
--		,case when drug_raw ilike concat('%',in_name,'%') then 1 end as contains_
	from rxnorm_base 
	where match_rank <> 100
	and match_rank is not null
)
,
approximates_transformed as (
	select *,
		round(1 - (levenstein_score_p / max_len_drug_p),2) as nls_p,
		round(1 - (levenstein_score_s / max_len_drug_s),2) as nls_s,
		size(ARRAY_INTERSECT(ingredient_tokens, drug_tokens)) / least(size(ingredient_tokens), size(drug_tokens)) as token_overlap_score_p,
		size(ARRAY_INTERSECT(ingredient_tokens, prod_ai_tokens)) / least(size(ingredient_tokens), size(prod_ai_tokens)) as token_overlap_score_s,
		case when soundex_drug = soundex_in then 1 end as sm_dr_in,
		case when soundex_in = soundex_prod_ai then 1 end as sm_pa_in
	from approximates
)
,
approximates_matching as (
	select *
	from approximates_transformed
	where nls_p >= 0.9
	or token_overlap_score_p >= 0.8
	or sm_dr_in = 1
	or nls_s >=0.9
	or token_overlap_score_s >= 0.8 
	or sm_pa_in = 1
)

select * from approximates_matching limit 10;

--select count(*), count(distinct drug_raw)
--from approximates_matching;


-- 11.
select count(distinct primaryid)
from pediatric_adr_events.raw_source.demo
where occr_country = 'US'; 

-- 12.
with us_drug_cases as (
	select distinct primaryid, drugname
	from pediatric_adr_events.raw_source.drug
	where primaryid in (
		select distinct primaryid
		from pediatric_adr_events.raw_source.demo
		where occr_country = 'US'
	)
)
,
drug_raw as (
	select 
		trim(regexp_replace(lower(drugname),'[\\[\\]]', '')) as drug_n,
		trim(regexp_replace(lower(prod_ai),'[\\[\\]]', '')) as prod_ai
	from pediatric_adr_events.raw_source.drug
)
,
rxnorm_clean as (
	select distinct 
		trim(regexp_replace(lower(drug_raw), '[\\[\\]]', '')) as drug_raw,	
		trim(regexp_replace(lower(in_name), '[\\[\\]]', '')) as in_name,
		match_rank,
		match_score,
		match_source
	from pediatric_adr_events.raw_source.rxnorm_key
	where added_datetime like '2026-05-18%' -- sampling for now
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
	from rxnorm_clean rk
	left join drug_raw dr
	on dr.drug_n = rk.drug_raw
)
,
approximates as(
	select 
		*, 
		LEVENSHTEIN(drug_raw, in_name) as levenstein_score_p, 
		greatest(length(drug_raw), length(in_name)) as max_len_drug_p,
		LEVENSHTEIN(prod_ai, in_name) as levenstein_score_s, 
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
--		,case when drug_raw ilike concat('%',in_name,'%') then 1 end as contains_
	from rxnorm_base 
	where match_rank <> 100
	and match_rank is not null
)
,
approximates_transformed as (
	select *,
		round(1 - (levenstein_score_p / max_len_drug_p),2) as nls_p,
		round(1 - (levenstein_score_s / max_len_drug_s),2) as nls_s,
		size(ARRAY_INTERSECT(ingredient_tokens, drug_tokens)) / least(size(ingredient_tokens), size(drug_tokens)) as token_overlap_score_p,
		size(ARRAY_INTERSECT(ingredient_tokens, prod_ai_tokens)) / least(size(ingredient_tokens), size(prod_ai_tokens)) as token_overlap_score_s,
		case when soundex_drug = soundex_in then 1 end as sm_dr_in,
		case when soundex_in = soundex_prod_ai then 1 end as sm_pa_in
	from approximates
)
,
approximates_matching as (
	select *
	from approximates_transformed
	where nls_p >= 0.9
	or token_overlap_score_p >= 0.8
	or sm_dr_in = 1
	or nls_s >=0.9
	or token_overlap_score_s >= 0.8 
	or sm_pa_in = 1
)

select count(*), count(distinct primaryid)
from us_drug_cases
where drugname in (
	select distinct drug_raw
	from approximates_matching
	union
	select distinct drug_raw
	from pediatric_adr_events.raw_source.rxnorm_key
	where match_rank = 100 or match_rank is null 
	and drug_raw <> 'dummy'
);

