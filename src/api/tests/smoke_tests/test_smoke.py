import json
import os

import pytest
import requests

from test_helpers.terraform import read_terraform_output

from .utils import execute_smoke_test, get_app_key, get_base_url, get_headers


def _request(base_url: str, headers: dict, path: str, method: str):
    url = f"{base_url}{path}"
    if method == "POST":
        body = json.dumps({"foo": "bar"})
        return requests.post(url=url, headers=headers, data=body)
    elif method == "DELETE":
        return requests.delete(url=url, headers=headers)

    return requests.get(url=url, headers=headers)


@pytest.mark.smoke
@pytest.mark.parametrize(
    "request_details",
    [
        [
            "/_status",
            "GET",
            200,
        ],
        [
            "/ProductTeam",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateProductTeamIncomingParams.ods_code: field required",
                "CreateProductTeamIncomingParams.name: field required",
                "CreateProductTeamIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeam/123/Product",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateCpmProductIncomingParams.name: field required",
                "CreateCpmProductIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeam/123",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeam/123/Product/abc",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeam/123/Product/abc",
            "DELETE",
            404,
        ],
        [
            "/ProductTeam/123",
            "DELETE",
            404,
        ],
        [
            "/Product",
            "GET",
            400,
            ["VALIDATION_ERROR"],
            [
                "SearchProductQueryParams.__root__: Please provide exactly one valid query parameter: ('product_team_id', 'organisation_code')."
            ],
        ],
    ],
)
def test_smoke_tests(request_details):
    workspace = os.environ.get("WORKSPACE") or read_terraform_output("workspace.value")
    environment = os.environ.get("ACCOUNT") or read_terraform_output(
        "environment.value"
    )
    app_key = get_app_key(environment=environment)
    headers = get_headers(app_key=app_key)
    base_url = get_base_url(workspace=workspace, environment=environment)
    print(  # noqa: T201
        f"🏃 Running 🏃 smoke test ({environment}.{workspace} --> {base_url}{request_details[0]}) - 🤔"
    )

    execute_smoke_test(
        request_method=_request,
        base_url=base_url,
        headers=headers,
        request_details=request_details,
    )
