import json
from uuid import uuid4

import boto3
import pytest
import requests
from event.json import json_loads

from test_helpers.sample_data import ORGANISATION
from test_helpers.terraform import read_terraform_output


class SmokeTestError(Exception):
    pass


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

PERSISTENT_ENVS = ["dev", "qa", "int", "prod", "ref"]


def is_2xx(status_code: int):
    return 200 <= status_code < 300


def item_already_exists(response: requests.Response):
    response_text = json_loads(response.text)
    if response_text["issue"][0]["diagnostics"] == "Item already exists":
        return True
    return False


def create_organization(base_url: str, headers: dict):
    organisation_body = json.dumps(ORGANISATION)
    url = f"{base_url}/Organization"
    return requests.post(url=url, headers=headers, data=organisation_body)


def read_organization(base_url: str, headers: dict):
    org_id = "f9518c12-6c83-4544-97db-d9dd1d64da97"
    url = f"{base_url}/Organization/{org_id}"
    return requests.get(url=url, headers=headers)


# def create_device(base_url: str, headers: dict, context: dict):
#     device_body = json.dumps(DEVICE)
#     url = f"{base_url}/Device"
#     response = requests.post(url=url, headers=headers, data=device_body)
#     context["device_id"] = response.headers["Location"]
#     return response

# def read_device(base_url: str, headers: dict, context: dict):
#     created_device_id = context["device_id"]
#     url = f"{base_url}/Device/{created_device_id}"
#     return requests.get(url=url, headers=headers)


REQUEST_METHODS = [
    create_organization,
    # create_device,
    read_organization,
    # read_device
    # delete_device - we need this in order to clean up the tests
]


def create_apigee_url(apigee_env: str, workspace: str):
    base_url = ".".join(filter(bool, (apigee_env, APIGEE_BASE_URL)))
    return f"https://{base_url}/cpm-{workspace}"


def _prepare_base_request(workspace: str) -> tuple[str, dict]:
    client = boto3.client("secretsmanager")
    workspace = "dev" if workspace not in PERSISTENT_ENVS else workspace

    secret_name = f"{workspace}-apigee-app-key"

    secret = client.get_secret_value(SecretId=secret_name)
    appkey = secret["SecretString"]

    apigee_env = APIGEE_ENV_FOR_WORKSPACE[workspace]
    base_url = create_apigee_url(
        apigee_env=apigee_env if apigee_env != "prod" else "", workspace=workspace
    )
    headers = {
        "accept": "application/json",
        "version": "1",
        "authorization": "letmein",
        "apikey": appkey,
        "x-correlation-id": f"SMOKE:{uuid4()}",
        "x-request-id": f"{uuid4()}",
    }
    return base_url, headers


@pytest.mark.smoke
def test_smoke_tests():
    print("🏃 Running 🏃 smoke test - 🤔")  # noqa: T201
    workspace = read_terraform_output("workspace.value")
    base_url, headers = _prepare_base_request(workspace=workspace)
    for request_method in REQUEST_METHODS:
        response = request_method(base_url=base_url, headers=headers)
        if is_2xx(response.status_code) or item_already_exists(response):
            print(  # noqa: T201
                f"🎉🎉 - Your 💨 Smoke 💨 test for method '{request_method.__name__}' has passed - 🎉🎉"
            )
        else:
            raise SmokeTestError(
                f"The smoke test for method '{request_method.__name__}' "
                f"has failed with status code {response.status_code} 😭😭\n"
                f"{response.json()}"
            )
