from typing import Tuple, Any, Dict
from time import sleep
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore

import os


def requests_retry_session(
    retries: int = 3,
    backoff_factor: float = 1.5,
    status_forcelist: Tuple[int, int, int, int] = (500, 502, 503, 504),
    session: requests.Session | None = None,
) -> requests.Session:
    session = session or requests.Session()
    # Replace type Any with callable
    retry: Any = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def api_call(url: str) -> Dict[str, Any] | None:
    api_key = os.getenv("API_KEY")
    request_header = {
        "Accept": "application/json",
        "X-API-Key": api_key,
    }
    try:
        response = requests_retry_session().get(url, headers=request_header)

        if response.headers.get("X-Rate-Limit-Remaining"):
            if int(response.headers.get("X-Rate-Limit-Remaining", 0)) == 0:
                sleep(0.5)

        if not response.status_code == 200:
            return None

        return response.json()
    except requests.exceptions.RequestException as e:
        # replace with logging module and httperror
        print(f"Error calling api: {e}")
        return None
