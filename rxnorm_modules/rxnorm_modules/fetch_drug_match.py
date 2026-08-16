import requests
from requests.exceptions import HTTPError
from pediatric_adr_shared.logging_mod import init_logger

logger = init_logger("fetch_drug_match")


def get_exact_string_match(drug_str: str) -> list[int]:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    headers_ls = {"name": drug_str, "search": 0}
    res = requests.get(BASE_URL, params=headers_ls)
    try:
        res.raise_for_status()
        content = res.json()
        top_obj = content["idGroup"]
        if "rxnormId" in top_obj:
            logger.info(f"An exact match found for {drug_str}")
            rxcui_ls = top_obj["rxnormId"] if "rxnormId" in top_obj else None
            drug_info = {
                "drug_raw": drug_str,
                "match_rxcui": rxcui_ls,
                "match_rank": 100 if rxcui_ls is not None else None,
                "match_score": 100,
                "match_name": None,
                "match_source": "RxNorm" if rxcui_ls is not None else None,
            }
        else:
            drug_info = None
        return drug_info
    except HTTPError as err:
        logger.error(f"HTTP Error-> {err}")
    except Exception as e:
        logger.error(f"Unexpected error found -> {e}")


def get_approximate_result(drug_str: str) -> dict:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
    header_list = {"term": drug_str, "option": 1}
    res = requests.get(BASE_URL, params=header_list)
    try:
        res.raise_for_status()
        content = res.json()
        top_obj = content["approximateGroup"]
        if "candidate" in top_obj:
            top_candidate = top_obj["candidate"][0]
            drug_info = {
                "drug_raw": drug_str,
                "match_rxcui": top_candidate["rxcui"],
                "match_rank": int(top_candidate["rank"]),
                "match_score": float(top_candidate["score"]),
                "match_name": top_candidate.get("name", None),
                "match_source": top_candidate["source"],
            }
        else:  # if drug is not RxNorm then return None
            drug_info = {
                "drug_raw": drug_str,
                "match_rxcui": None,
                "match_rank": None,
                "match_name": None,
                "match_source": None,
            }
        return drug_info
    except HTTPError as err:
        logger.error(f"HTTP Error-> {err}")
    except Exception as e:
        logger.error(f"Unexpected error found -> {e}")


def get_term_info(drug_str: str, rxcui_index: int) -> dict:
    BASE_URL = (
        f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui_index}/related.json?tty=BN+IN"
    )
    entity_assume = {"rxcui": None, "name": drug_str}
    res = requests.get(BASE_URL)
    try:
        res.raise_for_status()
        content = res.json()
        brand_entity = (
            content["relatedGroup"]["conceptGroup"][0]
            if content["relatedGroup"]["conceptGroup"][0]["tty"] == "BN"
            else content["relatedGroup"]["conceptGroup"][-1]
        )
        ingr_entity = (
            content["relatedGroup"]["conceptGroup"][-1]
            if content["relatedGroup"]["conceptGroup"][-1]["tty"] == "IN"
            else content["relatedGroup"]["conceptGroup"][0]
        )
        brand_name = (
            brand_entity["conceptProperties"][0]
            if "conceptProperties" in brand_entity
            else entity_assume
        )
        ingredients_name = (
            ingr_entity["conceptProperties"][0]
            if "conceptProperties" in ingr_entity
            else entity_assume
        )
        bn_rxcui = brand_name["rxcui"]
        bn_name = brand_name["name"]
        in_rxcui = ingredients_name["rxcui"]
        in_name = ingredients_name["name"]
        return_dict = {
            "bn_rxcui": int(bn_rxcui) if bn_rxcui is not None else None,
            "bn_name": bn_name,
            "in_rxcui": int(in_rxcui) if in_rxcui is not None else None,
            "in_name": in_name,
        }
        return return_dict
    except HTTPError as err:
        logger.error(f"HTTP Error-> {err}")
    except Exception as e:
        logger.error(f"Unexpected error found -> {e}")


def none_rxnorm_default_dict(drug_name: str) -> dict:
    return {
        "bn_rxcui": None,
        "bn_name": None,
        "in_rxcui": None,
        "in_name": drug_name,
    }


def process_multi_drug_match(drug_match_d: dict, match_rxcui: int) -> dict:
    drug_info = {
        "drug_raw": drug_match_d["drug_raw"],
        "match_rxcui": match_rxcui,
        "match_rank": drug_match_d["match_rank"],
        "match_score": drug_match_d["match_score"],
        "match_name": drug_match_d["match_name"],
        "match_source": drug_match_d["match_source"],
    }
    return drug_info


def process_returns(drug_match_d: dict, drug_info_d: dict, rxcui: int | None) -> dict:
    drug_match_d.update(drug_info_d)
    return_drug_match = {
        "drug_raw": drug_match_d["drug_raw"],
        "match_rxcui": int(rxcui) if rxcui is not None else None,
        "match_rank": drug_match_d["match_rank"],
        "match_score": drug_match_d.get("match_score", None),
        "match_name": drug_match_d["match_name"],
        "match_source": drug_match_d["match_source"],
        "bn_rxcui": drug_match_d["bn_rxcui"],
        "bn_name": drug_match_d["bn_name"],
        "in_rxcui": drug_match_d["in_rxcui"],
        "in_name": drug_match_d["in_name"],
    }
    return return_drug_match


def get_drug_match(drug_str):
    logger.info(f"API call for drug {drug_str}")
    drug_match = get_exact_string_match(drug_str)
    if drug_match is None:
        drug_match = get_approximate_result(drug_str)
        logger.info(f"Falling back to approximate match for {drug_str}")
    print(drug_match)
    if drug_match["match_rxcui"] is not None:
        drug_hash = drug_match["match_rxcui"]
        if isinstance(drug_match["match_rxcui"], list) and len(drug_hash) > 1:
            logger.info(f"Found {len(drug_hash)} rxcui for {drug_str}")
            collect_matches = []
            for drug in drug_hash:
                drug_match = process_multi_drug_match(drug_match, int(drug))
                drug_info = get_term_info(drug_str, int(drug))
                drug_final = process_returns(drug_match, drug_info, int(drug))
                logger.info(f"Results for {drug_str}'s {drug} retrieved")
                collect_matches.append(drug_final)
            return collect_matches
        if isinstance(drug_hash, list) and len(drug_hash) == 1:
            drug_hash = int(drug_hash[0])
        logger.info(f"Found only 1 rxcui for {drug_str} -> {drug_hash}")
        drug_info = get_term_info(drug_str, drug_hash)
    else:
        drug_info = none_rxnorm_default_dict(drug_str)
        drug_hash = None
    return_drug_match = process_returns(drug_match, drug_info, drug_hash)
    logger.info(f"Results for {drug_str} retrieved")
    logger.info(f"Result dictionary -> {return_drug_match}\n")
    return return_drug_match
