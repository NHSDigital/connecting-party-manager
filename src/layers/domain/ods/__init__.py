import re
import time
from functools import wraps
from http import HTTPStatus
from typing import Callable, ParamSpec, TypeVar

import requests
from requests.exceptions import RequestException

ODS_API_BASE = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"
ODS_API_ENDPOINT = f"{ODS_API_BASE}/" "{ods_code}"
BACKOFF_BASE_SECONDS = 2
WHITESPACE = re.compile(r"^(\s+)$")


class InvalidOdsCodeError(Exception):
    def __init__(self, ods_code):
        super().__init__(
            f"Invalid ODS Code: could not resolve '{ODS_API_ENDPOINT.format(ods_code=ods_code)}'"
        )


class UnexpectedStatusCode(Exception):
    pass


class OdsApiOfflineError(ExceptionGroup):
    def __new__(cls, n_attempts: int, fn_name: str, exceptions: list):
        """
        This is the recommended pattern for deriving from ExceptionGroup,
        see https://docs.python.org/3/library/exceptions.html
        """
        self = super().__new__(
            OdsApiOfflineError,
            f"{n_attempts} exceptions were raised whilst attempting to execute '{fn_name}'",
            exceptions,
        )
        return self


def _construct_ods_url(ods_code: str) -> str:
    return ODS_API_ENDPOINT.format(ods_code=ods_code)


def _is_whitespace(item: str) -> bool:
    return WHITESPACE.match(item) is not None


T = TypeVar("T")
RT = TypeVar("RT")
P = ParamSpec("P")


def retry(max_attempts: int) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
    """Retrying on RequestException, with exponential back-off of 2*n seconds"""

    def decorator(fn: Callable[P, RT]) -> Callable[P, RT]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Callable[P, RT]:
            exceptions = []
            for n in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except RequestException as exc:
                    exceptions.append(exc)
                finally:
                    time.sleep(BACKOFF_BASE_SECONDS**n)
            raise OdsApiOfflineError(n, fn.__name__, exceptions)

        return wrapper

    return decorator


@retry(max_attempts=3)
def is_valid_ods_code(ods_code: str) -> bool:
    if _is_whitespace(ods_code):
        return False

    url = _construct_ods_url(ods_code=ods_code)
    response = requests.get(url=url)
    status_code = HTTPStatus(response.status_code)

    if status_code is HTTPStatus.OK:
        return True
    if HTTPStatus.BAD_REQUEST <= status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
        return False
    if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        response.raise_for_status()
    raise UnexpectedStatusCode(
        f"Received unexpected status code '{status_code}' "
        f"from {ODS_API_ENDPOINT} "
        f"for ODS code '{ods_code}'"
    )


def validate_ods_code(ods_code: str):
    if not is_valid_ods_code(ods_code=ods_code):
        raise InvalidOdsCodeError(ods_code=ods_code)
