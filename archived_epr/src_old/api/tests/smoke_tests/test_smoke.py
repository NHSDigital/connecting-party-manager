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
            "/ProductTeamEpr",
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
            "/ProductTeamEpr/123/ProductEpr",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateCpmProductIncomingParams.name: field required",
                "CreateCpmProductIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateCpmProductIncomingParams.name: field required",
                "CreateCpmProductIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc",
            "DELETE",
            404,
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/DeviceReferenceData",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateDeviceReferenceDataIncomingParams.name: field required",
                "CreateDeviceReferenceDataIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateDeviceReferenceDataIncomingParams.name: field required",
                "CreateDeviceReferenceDataIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/DeviceReferenceData/MhsMessageSet",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateDeviceReferenceDataIncomingParams.name: field required",
                "CreateDeviceReferenceDataIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/Device",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateDeviceIncomingParams.name: field required",
                "CreateDeviceIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/Device/MessageHandlingSystem",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateMhsDeviceIncomingParams.questionnaire_responses: field required",
                "CreateMhsDeviceIncomingParams.foo: extra fields not permitted",
            ],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/Device/AccreditedSystem",
            "POST",
            400,
            ["MISSING_VALUE", "VALIDATION_ERROR"],
            [
                "CreateAsDeviceIncomingParams.questionnaire_responses: field required",
                "CreateAsDeviceIncomingParams.foo: extra fields not permitted",
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
            "/ProductTeamEpr/123",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeamEpr/123/Product",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/DeviceReferenceData",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/DeviceReferenceData/xyz",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/ProductTeamEpr/123/ProductEpr/abc/dev/Device/xyz",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find ProductTeam for key ('123')"],
        ],
        [
            "/Questionnaire/987",
            "GET",
            404,
            ["RESOURCE_NOT_FOUND"],
            ["Could not find Questionnaire for key ('987')"],
        ],
        [
            "/searchSdsDevice",
            "GET",
            400,
            ["MISSING_VALUE"],
            [
                "SearchSDSDeviceQueryParams.nhs_as_client: field required",
                "SearchSDSDeviceQueryParams.nhs_as_svc_ia: field required",
            ],
        ],
        [
            "/searchSdsEndpoint",
            "GET",
            400,
            ["VALIDATION_ERROR"],
            [
                "SearchSDSEndpointQueryParams.__root__: At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key"
            ],
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
