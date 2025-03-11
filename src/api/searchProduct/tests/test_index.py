import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

from conftest import dynamodb_client_with_sleep
from test_helpers.response_assertions import _response_assertions
from test_helpers.terraform import read_terraform_output
from test_helpers.validate_search_response import validate_product_result_body

VERSION = "1"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_TEAM_ID = "sample_product_team_id"
PRODUCT_TEAM_KEYS = [
    {"key_type": "product_team_id", "key_value": "808a36db-a52a-4130-b71e-d9cbcbaed15b"}
]
PRODUCT_NAME = "product-name"
PRODUCT_ID = "P.AAA-367"

ALLOWED_PARAMS = ("product_team_id", "organisation_code")


def _create_org():
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    return product_team


@pytest.mark.integration
def test_no_results():
    product_team = _create_org()
    product_team_id = product_team.id
    params = {"product_team_id": product_team_id}

    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client

        pt_repo = ProductTeamRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        pt_repo.write(entity=product_team)

        result = product_handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    expected_result = json.dumps({"results": []})
    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": VERSION,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
def test_search_by_product_team_id():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(name=PRODUCT_TEAM_NAME)
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team)

    cpm_product = product_team.create_cpm_product(
        name=PRODUCT_NAME, product_id=PRODUCT_ID
    )

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )
        product_repo.write(cpm_product)

        params = {"product_team_id": str(product_team.id)}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    expected_result = json.dumps(
        {
            "results": [
                {
                    "org_code": ODS_CODE,
                    "product_teams": [
                        {
                            "product_team_id": None,
                            "cpm_product_team_id": product_team.id,
                            "products": [cpm_product.state()],
                        },
                    ],
                }
            ]
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": VERSION,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
def test_search_by_product_team_alias():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team)

    cpm_product = product_team.create_cpm_product(
        name=PRODUCT_NAME, product_id=PRODUCT_ID
    )

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )
        product_repo.write(cpm_product)

        params = {"product_team_id": "808a36db-a52a-4130-b71e-d9cbcbaed15b"}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    expected_result = json.dumps(
        {
            "results": [
                {
                    "org_code": ODS_CODE,
                    "product_teams": [
                        {
                            "product_team_id": "808a36db-a52a-4130-b71e-d9cbcbaed15b",
                            "cpm_product_team_id": product_team.id,
                            "products": [cpm_product.state()],
                        },
                    ],
                }
            ]
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": VERSION,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
def test_index_org_code():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team)

    # Create a product under the product team
    cpm_product = product_team.create_cpm_product(
        name=PRODUCT_NAME, product_id=PRODUCT_ID
    )

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )
        product_repo.write(cpm_product)

        params = {"organisation_code": ODS_CODE}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    expected_result = json.dumps(
        {
            "results": [
                {
                    "org_code": ODS_CODE,
                    "product_teams": [
                        {
                            "product_team_id": "808a36db-a52a-4130-b71e-d9cbcbaed15b",
                            "cpm_product_team_id": product_team.id,
                            "products": [cpm_product.state()],
                        },
                    ],
                }
            ]
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": VERSION,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
def test_search_multiple():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(name=PRODUCT_TEAM_NAME)
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team)

    cpm_product = product_team.create_cpm_product(
        name=PRODUCT_NAME, product_id=PRODUCT_ID
    )
    cpm_product_2 = product_team.create_cpm_product(name="product 2")
    cpm_product_3 = product_team.create_cpm_product(name="product 3")

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )
        product_repo.write(cpm_product)
        product_repo.write(cpm_product_2)
        product_repo.write(cpm_product_3)

        params = {"product_team_id": str(product_team.id)}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    assert result["statusCode"] == 200
    result_body = json_loads(result["body"])
    assert "results" in result_body
    assert isinstance(result_body["results"], list)
    validate_product_result_body(
        result_body["results"][0]["product_teams"][0]["products"],
        [product.state() for product in [cpm_product, cpm_product_2, cpm_product_3]],
    )


@pytest.mark.integration
def test_index_org_code_multiple_product_teams():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team_1 = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    product_team_2 = org.create_product_team(name="product team name 2")
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team_1)
    product_team_repo.write(entity=product_team_2)

    # Create a product under each of the product teams
    cpm_product_1 = product_team_1.create_cpm_product(name=PRODUCT_NAME)
    cpm_product_2 = product_team_2.create_cpm_product(name="product name 2")

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )
        product_repo.write(cpm_product_1)
        product_repo.write(cpm_product_2)

        params = {"organisation_code": ODS_CODE}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    response_data = json_loads(result["body"])

    # Expected response structure (without enforcing order)
    expected_response = {
        "results": [
            {
                "org_code": ODS_CODE,
                "product_teams": [
                    {
                        "product_team_id": "808a36db-a52a-4130-b71e-d9cbcbaed15b",
                        "cpm_product_team_id": product_team_1.id,
                        "products": [cpm_product_1.state()],
                    },
                    {
                        "product_team_id": None,
                        "cpm_product_team_id": product_team_2.id,
                        "products": [cpm_product_2.state()],
                    },
                ],
            }
        ]
    }

    # Ensure expected product teams are sorted
    expected_product_teams = sorted(
        expected_response["results"][0]["product_teams"],
        key=lambda team: team["cpm_product_team_id"],
    )
    # Sort the products within each product team in the expected response
    for team in expected_product_teams:
        team["products"] = sorted(team["products"], key=lambda product: product["id"])

    # Extract response product teams (no sorting needed)
    response_product_teams = response_data["results"][0]["product_teams"]

    # Perform assertion
    assert response_data["results"][0]["org_code"] == ODS_CODE
    assert response_product_teams == expected_product_teams


@pytest.mark.integration
@pytest.mark.parametrize(
    "query_params, expected_status, expected_error",
    [
        (
            None,
            400,
            f"SearchProductQueryParams.__root__: Please provide exactly one valid query parameter: {ALLOWED_PARAMS}.",
        ),
        (
            {"organisation_code": "ODS_CODE", "product_team_id": "PRODUCT_TEAM_ID"},
            400,
            f"SearchProductQueryParams.__root__: Please provide exactly one valid query parameter: {ALLOWED_PARAMS}.",
        ),
        (
            {"organisation_code": "ODS_CODE", "FOO": "BAR"},
            400,
            "SearchProductQueryParams.FOO: extra fields not permitted",
        ),
    ],
)
def test_index_invalid_query_params(query_params, expected_status, expected_error):
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")
    client = dynamodb_client_with_sleep()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import cache as product_cache
        from api.searchProduct.index import handler as handler

        product_cache["DYNAMODB_CLIENT"] = client

        CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": query_params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == expected_status
    assert result_body["errors"][0]["code"] == "VALIDATION_ERROR"
    assert result_body["errors"][0]["message"] == expected_error


@pytest.mark.integration
def test_index_no_product_team():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import handler

        params = {"product_team_id": PRODUCT_TEAM_ID}
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 200
    assert result_body == {"results": []}


@pytest.mark.integration
def test_index_no_org():
    table_name = read_terraform_output("dynamodb_cpm_table_name.value")

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import handler

        params = {
            "organisation_code": ODS_CODE,
        }
        result = handler(
            event={
                "headers": {"version": VERSION},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 200
    assert result_body == {"results": []}
