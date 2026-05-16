import requests, requests.exceptions as re_e
import re
from datetime import datetime
from bs4 import BeautifulSoup
from pediatric_adr_shared.logging_mod import init_logger

ROOT_URL = "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html"
PATTERN = re.compile(r"faers_ascii_(\d{4})[qQ]([1-4])\.zip", re.IGNORECASE)

logger = init_logger()


def check_page_response(url: str = ROOT_URL) -> requests.models.Response:
    res = requests.get(url)
    return res


def get_latest_url(response: requests.models.Response, year: int, quarter: int) -> str:
    soup = BeautifulSoup(response.text, "html.parser")
    extr_url = [
        a["href"]
        for a in soup.select('a[href*="faers_ascii_"]')
        if all(str(i) in a["href"].lower() for i in [year, quarter])
    ]
    return extr_url


def operation():
    today = datetime.now()
    year = today.year
    quarter = f"q{round(today.month / 3) - 1}"  # considering the past month since data is historical
    res_ = check_page_response()
    try:
        res_.raise_for_status()
        outc_url = get_latest_url(res_, year, quarter)
        if len(outc_url) > 0:
            logger.info(f"Retrieved latest quarter URL -> {outc_url}")
            return outc_url[0]
        else:
            logger.error("URL not available")
            RuntimeError()
    except re_e.HTTPError as httperr:
        logger.error(f"HTTP error occured: {httperr}")
    except Exception as err:
        logger.error(f"Other error occured: {err}")


if __name__ == "__main__":
    operation()
