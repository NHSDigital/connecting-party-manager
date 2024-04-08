import json

import pytest
import requests

from test_helpers.sample_data import ORGANISATION
from test_helpers.terraform import read_terraform_output

from .utils import execute_smoke_test, get_app_key, get_base_url, get_headers


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


@pytest.mark.smoke
def test_smoke_tests():
    workspace = read_terraform_output("workspace.value")
    environment = read_terraform_output("environment.value")
    app_key = get_app_key(environment=environment)
    headers = get_headers(app_key=app_key)
    base_url = get_base_url(workspace=workspace, environment=environment)
    print(  # noqa: T201
        f"🏃 Running 🏃 smoke test ({environment}.{workspace} --> {base_url}) - 🤔"
    )

    for request_method in REQUEST_METHODS:
        execute_smoke_test(
            request_method=request_method, base_url=base_url, headers=headers
        )
