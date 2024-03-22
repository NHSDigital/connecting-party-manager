import json
from uuid import uuid4

import boto3
import fire
import pytest
import requests

from test_helpers.sample_data import DEVICE, ORGANISATION

APIGEE_BASE_URL = "api.service.nhs.uk"

APIGEE_ENV_FOR_WORKSPACE = {
    "dev": "internal-dev",
    "dev-sandbox": "internal-dev-sandbox",
    "qa": "internal-qa",
    "qa-sandbox": "internal-qa-sandbox",
    "ref": "ref",
    "int": "int",
    "int-sandbox": "sandbox",
    "prod": "prod",
}


def is_2xx(status_code: int):
    return 200 <= status_code < 300


def item_already_exists(response: requests.Response):
    response_content = response.text


def create_organization(base_url: str, headers: dict):
    organisation_body = json.dumps(ORGANISATION)
    url = f"{base_url}/Organization"
    return requests.post(url=url, headers=headers, data=organisation_body)


def create_device(base_url: str, headers: dict):
    device_body = json.dumps(DEVICE)
    url = f"{base_url}/Device"
    return requests.post(url=url, headers=headers, data=device_body)


REQUEST_METHODS = {create_organization, create_device}


def create_apigee_url(apigee_env: str):
    base_url = ".".join(filter(bool, (apigee_env, APIGEE_BASE_URL)))
    return f"https://{base_url}/cpm-{apigee_env}"


def _prepare_base_request(workspace: str, actor: str, client) -> tuple[str, dict]:
    secret_name = f"{workspace}-apigee-app-key"
    secret = client.get_secret_value(SecretId=secret_name)
    apikey = secret["SecretString"]

    apigee_env = APIGEE_ENV_FOR_WORKSPACE[workspace]
    base_url = create_apigee_url(
        apigee_env=apigee_env if apigee_env != "prod" else "", actor=actor
    )
    headers = {
        "accept": "application/json; version=1.0",
        "authorization": "letmein",
        "apikey": apikey,
        "x-correlation-id": f"SMOKE:{uuid4()}",
        "x-request-id": f"{uuid4()}",
    }
    return base_url, headers


@pytest.mark.smoke
def smoke_tests(workspace: str):
    CLIENT = boto3.client("secretsmanager")
    print("🏃 Running 🏃 smoke test - 🤔")  # noqa: T201
    base_url, headers = _prepare_base_request(workspace=workspace, client=CLIENT)
    for request_method in REQUEST_METHODS:
        response = request_method(base_url=base_url, headers=headers)
        if is_2xx(response.status_code) or item_already_exists(response):
            print(  # noqa: T201
                f"🎉🎉 - Your 💨 Smoke 💨 test for method '{request_method.__name__}' has passed - 🎉🎉"
            )
        else:
            raise fire.core.FireError(
                f"The smoke test for method '{request_method.__name__}' "
                f"has failed with status code {response.status_code} 😭😭\n"
                f"{response.json()}"
            )
