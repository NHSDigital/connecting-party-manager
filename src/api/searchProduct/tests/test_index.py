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

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_TEAM_ID = "sample_product_team_id"
PRODUCT_TEAM_KEYS = [{"key_type": "product_team_id_alias", "key_value": "BAR"}]
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"


def _create_org():
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    return product_team


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
@pytest.mark.integration
def test_no_results(version):
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
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    expected_result = json.dumps({"results": []})
    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "version,product",
    [
        ("1", {"name": "product-name-a", "id": "P.AAA-367"}),
        ("1", {"name": "product-name-b", "id": "P.CCC-679"}),
        ("1", {"name": "product-name-c", "id": "P.HHH-437"}),
        ("1", {"name": "product-name-d", "id": "P.JJJ-793"}),
    ],
)
def test_index_product_team_id(version, product):
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
        name=product["name"], product_id=product["id"]
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
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    expected_result = json.dumps({"results": [cpm_product.state()]})

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "version,product",
    [
        ("1", {"name": "product-name-a", "id": "P.AAA-367"}),
        ("1", {"name": "product-name-b", "id": "P.CCC-679"}),
        ("1", {"name": "product-name-c", "id": "P.HHH-437"}),
        ("1", {"name": "product-name-d", "id": "P.JJJ-793"}),
    ],
)
def test_index_org_code(version, product):
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
        name=product["name"], product_id=product["id"]
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
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    expected_result = json.dumps({"results": [cpm_product.state()]})

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_query_param_provided(version):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
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
                "headers": {"version": version},
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 400
    assert result_body == {
        "errors": [
            {
                "code": "VALIDATION_ERROR",
                "message": "At least one query parameter ('organisation_code' or 'product_team_id') must be provided.",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_too_many_query_param_provided(version):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
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
        params = {
            "organisation_code": ODS_CODE,
            "product_team_id": PRODUCT_TEAM_ID,
        }
        result = handler(
            event={"headers": {"version": version}, "queryStringParameters": params}
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 400
    assert result_body == {
        "errors": [
            {
                "code": "VALIDATION_ERROR",
                "message": "Only one query parameter is allowed: 'organisation_code' or 'product_team_id'.",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_too_many_query_param_provided(version):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
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
        params = {
            "organisation_code": ODS_CODE,
            "FOO": "BAR",
        }
        result = handler(
            event={"headers": {"version": version}, "queryStringParameters": params}
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 400
    assert result_body == {
        "errors": [
            {
                "code": "VALIDATION_ERROR",
                "message": "Invalid query parameter(s): FOO",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_product_team(version):
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
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 200
    assert result_body == {"results": []}


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_org(version):
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
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 200
    assert result_body == {"results": []}


@pytest.mark.integration
@pytest.mark.parametrize(
    "products",
    [
        [
            {"name": "product-name-a", "id": "P.AAA-367"},
            {"name": "product-name-b", "id": "P.CCC-679"},
            {"name": "product-name-c", "id": "P.HHH-437"},
            {"name": "product-name-d", "id": "P.JJJ-793"},
        ],
    ],
)
def test_index_multiple_returned(products):
    version = 1
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client_with_sleep()

    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_team_repo.write(entity=product_team)

    cpm_products = []
    for product in products:
        cpm_product = product_team.create_cpm_product(
            name=product["name"], product_id=product["id"]
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

            product_cache["DYNAMODB_CLIENT"] = client
            product_repo = CpmProductRepository(
                table_name=product_cache["DYNAMODB_TABLE"],
                dynamodb_client=product_cache["DYNAMODB_CLIENT"],
            )

            product_repo.write(cpm_product)
        cpm_products.append(cpm_product)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchProduct.index import handler

        params = {"product_team_id": str(product_team.id)}
        result = handler(
            event={
                "headers": {"version": version},
                "queryStringParameters": params,
            }
        )

    assert result["statusCode"] == 200
    result_body = json_loads(result["body"])
    assert "results" in result_body
    assert isinstance(result_body["results"], list)
    validate_product_result_body(
        result_body["results"], [cpm_product.state() for cpm_product in cpm_products]
    )
