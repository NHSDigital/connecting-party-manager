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
    assert result == r"Device/(?P<id1>[^\/]+)/(?P<id2>[^\/]+)?field=(?P<id3>[^\/]+)"


def test__parse_params_from_url():
    path_params, query_params, result = _parse_params_from_url(
        path_template="Device/{id1}/{id2}?field={id3}", path="Device/123/foo?field=hiya"
    )
    assert result is True
    assert path_params == {"id1": "123", "id2": "foo"}
    assert query_params == {"id3": "hiya"}


def test_parse_path_create_device():
    with api_lambda_environment_variables():
        import api.createDevice.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="Device",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.createDevice.index)


def test_parse_path_read_device():
    with api_lambda_environment_variables():
        import api.readDevice.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="Device/123",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"id": "123"}, {}, api.readDevice.index)


def test_parse_path_create_product_team():
    with api_lambda_environment_variables():
        import api.createProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="POST",
        path="Organization",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({}, {}, api.createProductTeam.index)


def test_parse_path_read_product_team():
    with api_lambda_environment_variables():
        import api.readProductTeam.index

        endpoint_lambda_mapping = get_endpoint_lambda_mapping()

    assert parse_api_path(
        method="GET",
        path="Organization/123",
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    ) == ({"id": "123"}, {}, api.readProductTeam.index)


def test_parse_path_error():
    with pytest.raises(EndpointConfigurationError):
        parse_api_path(method="GET", path="ProductTeam/123", endpoint_lambda_mapping={})
