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
    result = _template_to_regex("Device/{id1}/{id2}?field={id3}")
    assert result == r"^Device/(?P<id1>[^\/]+)/(?P<id2>[^\/]+)?field=(?P<id3>[^\/]+)$"


def test__parse_params_from_url():
    path_params, query_params, result = _parse_params_from_url(
        path_template="Device/{id1}/{id2}?field={id3}", path="Device/123/foo?field=hiya"
    )
    assert result is True
    assert path_params == {"id1": "123", "id2": "foo"}
    assert query_params == {"id3": "hiya"}


@pytest.mark.parametrize(
    ["path_template", "path"],
    [
        ("Device/{id1}/{id2}", "Device/123/foo/bar"),
        ("Device/{id1}/{id2}?field={id3}", "Device/123/foo/bar"),
    ],
)
def test__parse_params_from_url_fail(path_template: str, path: str):
    _, _, result = _parse_params_from_url(path_template=path_template, path=path)
    assert result is False


def test__parse_params_from_url_post_product():
    path_params, _, result = _parse_params_from_url(
        path_template="ProductTeamEpr/{product_team_id}/ProductEpr",
        path="ProductTeamEpr/123/ProductEpr",
    )
    assert result is True
    assert path_params == {"product_team_id": "123"}


def test_parse_path_create_product_team():
    with api_lambda_environment_variables():
        import api.createProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeam",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.createProductTeam.index)


def test_parse_path_create_product_team_epr():
    with api_lambda_environment_variables():
        import api.createProductTeamEpr.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.createProductTeamEpr.index)


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


def test_parse_path_read_product_team_epr():
    with api_lambda_environment_variables():
        import api.readProductTeamEpr.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.readProductTeamEpr.index)


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


# def test_parse_path_search_cpm_product():
#     with api_lambda_environment_variables():
#         import api.searchCpmProduct.index
#
#         endpoint_lambda_mapping = get_endpoint_lambda_mapping()
#
#     assert parse_api_path(
#         method="GET",
#         path="ProductTeam/123/Product",
#         endpoint_lambda_mapping=endpoint_lambda_mapping,
#     ) == ({"product_team_id": "123"}, {}, api.searchCpmProduct.index)
#
def test_parse_path_create_epr_product():
    with api_lambda_environment_variables():
        import api.createEprProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr/123/ProductEpr",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.createEprProduct.index)


def test_parse_path_read_epr_product():
    with api_lambda_environment_variables():
        import api.readEprProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123/ProductEpr/456",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123", "product_id": "456"}, {}, api.readEprProduct.index)


def test_parse_path_search_epr_product():
    with api_lambda_environment_variables():
        import api.searchEprProduct.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123/ProductEpr",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"product_team_id": "123"}, {}, api.searchEprProduct.index)


def test_parse_path_create_device():
    with api_lambda_environment_variables():
        import api.createDevice.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr/123/ProductEpr/456/dev/Device",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456", "environment": "dev"},
        {},
        api.createDevice.index,
    )


def test_parse_path_read_device():
    with api_lambda_environment_variables():
        import api.readDevice.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123/ProductEpr/456/dev/Device/789",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {
            "product_team_id": "123",
            "product_id": "456",
            "environment": "dev",
            "device_id": "789",
        },
        {},
        api.readDevice.index,
    )


def test_parse_path_create_device_reference_data():
    with api_lambda_environment_variables():
        import api.createDeviceReferenceData.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr/123/ProductEpr/456/dev/DeviceReferenceData",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456", "environment": "dev"},
        {},
        api.createDeviceReferenceData.index,
    )


def test_parse_path_read_device_reference_data():
    with api_lambda_environment_variables():
        import api.readDeviceReferenceData.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123/ProductEpr/456/dev/DeviceReferenceData/789",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {
            "product_team_id": "123",
            "product_id": "456",
            "environment": "dev",
            "device_reference_data_id": "789",
        },
        {},
        api.readDeviceReferenceData.index,
    )


def test_parse_path_search_device_reference_data():
    with api_lambda_environment_variables():
        import api.searchDeviceReferenceData.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="ProductTeamEpr/123/ProductEpr/456/dev/DeviceReferenceData",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456", "environment": "dev"},
        {},
        api.searchDeviceReferenceData.index,
    )


def test_parse_path_create_mhs_device():
    with api_lambda_environment_variables():
        import api.createDeviceMessageHandlingSystem.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr/123/ProductEpr/456/dev/Device/MessageHandlingSystem",  # pragma: allowlist secret
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456", "environment": "dev"},
        {},
        api.createDeviceMessageHandlingSystem.index,
    )


def test_parse_path_create_as_device():
    with api_lambda_environment_variables():
        import api.createDeviceAccreditedSystem.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="ProductTeamEpr/123/ProductEpr/456/dev/Device/AccreditedSystem",  # pragma: allowlist secret
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == (
        {"product_team_id": "123", "product_id": "456", "environment": "dev"},
        {},
        api.createDeviceAccreditedSystem.index,
    )


def test_parse_path_search_sds_device():
    with api_lambda_environment_variables():
        import api.searchSdsDevice.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="searchSdsDevice",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.searchSdsDevice.index)


def test_parse_path_search_sds_endpoint():
    with api_lambda_environment_variables():
        import api.searchSdsEndpoint.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="searchSdsEndpoint",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.searchSdsEndpoint.index)


def test_parse_path_error():
    with pytest.raises(EndpointConfigurationError):
        parse_api_path(method="GET", path="ProductTeam/123", endpoint_lambda_mapping={})
