import json
import os

import pytest
import requests

from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.terraform import read_terraform_output

from .utils import execute_smoke_test, get_app_key, get_base_url, get_headers


def create_and_read_product_team(base_url: str, headers: dict):
    product_team_body = json.dumps(CPM_PRODUCT_TEAM_NO_ID)
    url = f"{base_url}/ProductTeam"
    response = requests.post(url=url, headers=headers, data=product_team_body)
    response_body = response.json()
    url = f"{base_url}/ProductTeam/{response_body["id"]}"
    return requests.get(url=url, headers=headers)


REQUEST_METHODS = [
    create_and_read_product_team,
]


@pytest.mark.smoke
def test_smoke_tests():
    workspace = os.environ.get("WORKSPACE") or read_terraform_output("workspace.value")
    environment = os.environ.get("ACCOUNT") or read_terraform_output(
        "environment.value"
    )
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
