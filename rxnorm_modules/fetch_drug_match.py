import requests
from requests.exceptions import HTTPError


def get_approximate_result(drug_str: str) -> dict:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
    res = requests.get(BASE_URL, params={"term": drug_str})
    try:
        res.raise_for_status()
        content = res.json()
        top_candidate = content["approximateGroup"]["candidate"][0]
        return_dict = {
            "drug_raw": drug_str,
            "match_rxcui": int(top_candidate["rxcui"]),
            "match_rank": int(top_candidate["rank"]),
            "match_name": top_candidate.get("name", None),
            "match_source": top_candidate["source"],
        }
        return return_dict
    except HTTPError as err:
        print(f"HTTP Error-> {err}")
    except Exception as e:
        print(f"Unexpected error found -> {e}")


def get_term_info(rxcui_index: int) -> dict:
    BASE_URL = (
        f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui_index}/related.json?tty=BN+IN"
    )
    brand_entity_assume = {"rxcui": -1, "name": None}
    res = requests.get(BASE_URL)
    try:
        res.raise_for_status()
        content = res.json()
        brand_entity = (
            content["relatedGroup"]["conceptGroup"][0]
            if content["relatedGroup"]["conceptGroup"][0]["tty"] == "BN"
            else content["relatedGroup"]["conceptGroup"][-1]
        )
        brand_name = (
            brand_entity["conceptProperties"][0]
            if "conceptProperties" in brand_entity
            else brand_entity_assume
        )
        ingr_entity = (
            content["relatedGroup"]["conceptGroup"][-1]
            if content["relatedGroup"]["conceptGroup"][-1]["tty"] == "IN"
            else content["relatedGroup"]["conceptGroup"][0]
        )
        ingredients = ingr_entity["conceptProperties"][0]
        bn_rxcui = brand_name["rxcui"]
        bn_name = brand_name["name"]
        in_rxcui = ingredients["rxcui"]
        in_name = ingredients["name"]
        return_dict = {
            "bn_rxcui": int(bn_rxcui) if brand_name["rxcui"] != -1 else None,
            "bn_name": bn_name,
            "in_rxcui": int(in_rxcui),
            "in_name": in_name,
        }
        return return_dict
    except HTTPError as err:
        print(f"HTTP Error-> {err}")
    except Exception as e:
        print(f"Unexpected error found -> {e}")


def get_drug_match(drug_str):
    print(drug_str)
    drug_match = get_approximate_result(drug_str)
    drug_info = get_term_info(drug_match["match_rxcui"])
    drug_match.update(drug_info)
    print(f"Results for {drug_str} retrieved")
    return drug_match


if __name__ == "__main__":
    # drug_str = "Dupixent 300 mg/2 mL injection"
    drug_str = "ENALAPRIL"
    drug_match = get_approximate_result(drug_str)
    drug_info = get_term_info(drug_match["match_rxcui"])
    drug_match.update(drug_info)
    print(drug_match)
