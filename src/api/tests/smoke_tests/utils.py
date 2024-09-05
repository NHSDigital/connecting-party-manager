from types import FunctionType
from uuid import uuid4

import boto3
import requests

from .config import APIGEE_BASE_URL, APIGEE_URL_PREFIX_BY_ENVIRONMENT


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
    apigee_url_prefix = (
        APIGEE_URL_PREFIX_BY_ENVIRONMENT[workspace]
        if workspace == f"{environment}-sandbox"
        else APIGEE_URL_PREFIX_BY_ENVIRONMENT[environment]
    )
    base_url = ".".join(filter(bool, (apigee_url_prefix, APIGEE_BASE_URL)))
    return f"https://{base_url}/cpm-{workspace}"


def is_2xx(status_code: int):
    return 200 <= status_code < 300


def item_already_exists(response_json: dict) -> bool:
    issue = response_json.get("issue")
    _item_exists = issue and issue[0]["diagnostics"] == "Item already exists"
    return _item_exists


def execute_smoke_test(request_method: FunctionType, base_url: str, headers: str):
    response: requests.Response = request_method(base_url=base_url, headers=headers)

    try:
        response_json: dict = response.json()
    except requests.JSONDecodeError:
        response_json = None

    success = is_2xx(status_code=response.status_code) or (
        response_json and item_already_exists(response_json=response_json)
    )
    if success:
        print(  # noqa: T201
            f"🎉🎉 - 💨 Smoke 💨 test for method '{request_method.__name__}' has passed - 🎉🎉"
        )
    if not success:
        if response.status_code == 401:
            print(  # noqa: T201
                ">> Did you forget to manually register your app with the Apigee Product? <<"
            )
        raise SmokeTestError(
            f"The smoke test for method '{request_method.__name__}' "
            f"has failed with status code {response.status_code} 😭😭\n"
            f"{response_json or response.text}"
        )
