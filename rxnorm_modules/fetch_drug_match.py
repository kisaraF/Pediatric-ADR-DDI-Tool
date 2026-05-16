import requests
from requests.exceptions import HTTPError
from pediatric_adr_shared.logging_mod import init_logger

logger = init_logger("fetch_drug_match")


def get_approximate_result(drug_str: str) -> dict:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
    res = requests.get(BASE_URL, params={"term": drug_str})
    try:
        res.raise_for_status()
        content = res.json()
        top_obj = content["approximateGroup"]
        if "candidate" in top_obj:
            top_candidate = top_obj["candidate"][0]
            drug_info = {
                "drug_raw": drug_str,
                "match_rxcui": int(top_candidate["rxcui"]),
                "match_rank": int(top_candidate["rank"]),
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


def get_drug_match(drug_str):
    logger.info(f"API call for drug {drug_str}")
    drug_match = get_approximate_result(drug_str)
    if drug_match["match_rxcui"] is not None:
        drug_info = get_term_info(drug_str, drug_match["match_rxcui"])
    else:
        drug_info = none_rxnorm_default_dict(drug_str)
    drug_match.update(drug_info)
    logger.info(f"Results for {drug_str} retrieved")
    return drug_match


# if __name__ == "__main__":
#     # drug_str = "Dupixent 300 mg/2 mL injection"
#     drug_str = "ENALAPRIL"
#     drug_match = get_approximate_result(drug_str)
#     drug_info = get_term_info(drug_match["match_rxcui"])
#     drug_match.update(drug_info)
#     print(drug_match)
