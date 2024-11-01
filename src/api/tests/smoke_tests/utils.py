import time
from types import FunctionType
from uuid import uuid4

import boto3
import requests

from .config import (
    APIGEE_BASE_URL,
    APIGEE_URL_PREFIX_BY_ENVIRONMENT,
    PERSISTENT_ENVIRONMENTS,
)


class SmokeTestError(Exception):
    pass


def get_app_key(environment: str, project: str = "") -> str:
    client = boto3.client("secretsmanager")
    secret_name = f"{environment}-apigee{project}-app-key"
    secret = client.get_secret_value(SecretId=secret_name)
    return secret["SecretString"]


def get_headers(app_key: str) -> dict:
    return {
        "accept": "application/json",
        "version": "1",
        "authorization": "letmein",
        "apikey": app_key,
        "x-correlation-id": f"SMOKE:{uuid4()}",
        "x-request-id": f"{uuid4()}",
    }


def get_base_url(workspace: str, environment: str) -> str:
    api_name = "connecting-party-manager"
    apigee_url_prefix = (
        APIGEE_URL_PREFIX_BY_ENVIRONMENT[workspace]
        if workspace == f"{environment}-sandbox"
        else APIGEE_URL_PREFIX_BY_ENVIRONMENT[environment]
    )
    base_url = ".".join(filter(bool, (apigee_url_prefix, APIGEE_BASE_URL)))

    if workspace not in PERSISTENT_ENVIRONMENTS:
        api_name = workspace

    return f"https://{base_url}/{api_name}"


def is_2xx(status_code: int, expected_status_code: int):
    return 200 <= status_code < 300 and status_code == expected_status_code


def is_4xx(status_code: int, expected_status_code: int):
    return (
        400 <= status_code < 500 and status_code != 401
    ) and status_code == expected_status_code


def item_already_exists(response_json: dict) -> bool:
    issue = response_json.get("issue")
    _item_exists = issue and issue[0]["diagnostics"] == "Item already exists"
    return _item_exists


def raise_smoke_test_error(request_method, status_code, response_content):
    raise SmokeTestError(
        f"The smoke test for method '{request_method.__name__}' "
        f"failed with status code {status_code} 😭😭\n"
        f"{response_content}"
    )


def execute_smoke_test(
    request_method: FunctionType, base_url: str, headers: str, request_details: list
):
    retries = 0

    while retries < 5:
        response: requests.Response = request_method(
            base_url=base_url,
            headers=headers,
            path=request_details[0],
            method=request_details[1],
        )
        if response.status_code == 504:
            retries += 1
            time.sleep(2)
        else:
            return response  # Return on success or any other error code

    try:
        response_json: dict = response.json()
    except requests.JSONDecodeError:
        response_json = None

    success2xx = is_2xx(
        status_code=response.status_code, expected_status_code=request_details[2]
    )
    if success2xx:
        if response_json == request_details[3]:
            print(  # noqa: T201
                f"🎉🎉 - 💨 Smoke 💨 test for method '{request_method.__name__}' has passed - 🎉🎉"
            )
        else:
            raise_smoke_test_error(
                request_method, response.status_code, response_json or response.text
            )

    if not success2xx:
        if is_4xx(
            status_code=response.status_code, expected_status_code=request_details[2]
        ):
            error_assertion = all(
                response_error["code"] in request_details[3]
                and response_error["message"] in request_details[4]
                for response_error in response_json.get("errors", [])
            )
            if error_assertion:
                print(  # noqa: T201
                    f"🎉🎉 - 💨 Smoke 💨 test for method '{request_method.__name__}' has passed - 🎉🎉"
                )
            else:
                raise_smoke_test_error(
                    request_method, response.status_code, response_json or response.text
                )
        else:
            if response.status_code == 401:
                print(  # noqa: T201
                    ">> Did you forget to manually register your app with the Apigee Product? <<"
                )
            raise_smoke_test_error(
                request_method, response.status_code, response_json or response.text
            )
