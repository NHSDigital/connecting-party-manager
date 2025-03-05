import os
from contextlib import contextmanager
from unittest import mock

import pytest

from api.tests.feature_tests.steps.endpoint_lambda_mapping import (
    EndpointConfigurationError,
    _parse_params_from_url,
    _template_to_regex,
    get_endpoint_lambda_mapping,
    parse_api_path,
)


@contextmanager
def api_lambda_environment_variables():
    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": "hiya",
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        yield


def test__template_to_regex():
    result = _template_to_regex("Product/{id1}/{id2}?field={id3}")
    assert result == r"^Product/(?P<id1>[^\/]+)/(?P<id2>[^\/]+)?field=(?P<id3>[^\/]+)$"


def test__parse_params_from_url():
    path_params, query_params, result = _parse_params_from_url(
        path_template="Product/{id1}/{id2}?field={id3}",
        path="Product/123/foo?field=hiya",
    )
    assert result is True
    assert path_params == {"id1": "123", "id2": "foo"}
    assert query_params == {"id3": "hiya"}


@pytest.mark.parametrize(
    ["path_template", "path"],
    [
        ("Product/{id1}/{id2}", "Product/123/foo/bar"),
        ("Product/{id1}/{id2}?field={id3}", "Product/123/foo/bar"),
    ],
)
def test__parse_params_from_url_fail(path_template: str, path: str):
    _, _, result = _parse_params_from_url(path_template=path_template, path=path)
    assert result is False


def test_parse_path_create_product_team():
    with api_lambda_environment_variables():
        import api.createProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeam",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.createProductTeam.index)


def test_parse_path_read_product_team():
    with api_lambda_environment_variables():
        import api.readProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeam/123",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.readProductTeam.index)


def test_parse_path_delete_product_team():
    with api_lambda_environment_variables():
        import api.deleteProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="DELETE",
        path="ProductTeam/123",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.deleteProductTeam.index)


def test_parse_path_create_cpm_product():
    with api_lambda_environment_variables():
        import api.createCpmProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeam/123/Product",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.createCpmProduct.index)


def test_parse_path_read_cpm_product():
    with api_lambda_environment_variables():
        import api.readCpmProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeam/123/Product/456",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123", "product_id": "456"}, {}, api.readCpmProduct.index)


def test_parse_path_delete_cpm_product():
    with api_lambda_environment_variables():
        import api.deleteCpmProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="DELETE",
        path="ProductTeam/123/Product/456",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456"},
        {},
        api.deleteCpmProduct.index,
    )


def test_parse_path_search_cpm_product():
    with api_lambda_environment_variables():
        import api.searchProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="Product",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.searchProduct.index)


def test_parse_path_error():
    with pytest.raises(EndpointConfigurationError):
        parse_api_path(method="GET", path="ProductTeam/123", endpoint_lambda_mapping={})
