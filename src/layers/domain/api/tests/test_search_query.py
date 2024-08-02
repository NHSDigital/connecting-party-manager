import pytest
from domain.api.query import SearchSDSDeviceQueryParams, SearchSDSEndpointQueryParams
from pydantic import ValidationError


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "nhs_as_client": "foo",
                "nhs_as_svc_ia": "foo",
            }
        ),
        (
            {
                "nhs_as_client": "foo",
                "nhs_as_svc_ia": "foo",
                "nhs_mhs_manufacturer_org": "foo",
            }
        ),
        ({"nhs_as_client": "foo", "nhs_as_svc_ia": "foo", "nhs_mhs_party_key": "foo"}),
        (
            {
                "nhs_as_client": "foo",
                "nhs_as_svc_ia": "foo",
                "nhs_mhs_manufacturer_org": "foo",
                "nhs_mhs_party_key": "foo",
            }
        ),
    ],
)
def test_device_query_accepted(params):
    search = SearchSDSDeviceQueryParams(**params)
    assert isinstance(search, SearchSDSDeviceQueryParams)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "nhs_as_client": "foo",
            }
        ),
        (
            {
                "nhs_as_svc_ia": "foo",
            }
        ),
        ({"nhs_as_client": "foo", "nhs_mhs_manufacturer_org": "foo"}),
        ({"nhs_as_svc_ia": "foo", "nhs_mhs_manufacturer_org": "foo"}),
        (
            {
                "nhs_as_client": "foo",
                "nhs_as_svc_ia": "foo",
                "foo": "bar",
            }
        ),
    ],
)
def test_device_query_invalid(params):
    with pytest.raises(ValidationError):
        search = SearchSDSDeviceQueryParams(**params)


@pytest.mark.parametrize(
    "params",
    [
        ({"nhs_id_code": "foo", "nhs_mhs_svc_ia": "foo"}),
        ({"nhs_id_code": "foo", "nhs_mhs_svc_ia": "foo", "nhs_mhs_party_key": "foo"}),
        ({"nhs_id_code": "foo", "nhs_mhs_party_key": "foo"}),
        ({"nhs_mhs_svc_ia": "foo", "nhs_mhs_party_key": "foo"}),
    ],
)
def test_endpoint_query_accepted(params):
    search = SearchSDSEndpointQueryParams(**params)
    assert isinstance(search, SearchSDSEndpointQueryParams)


@pytest.mark.parametrize(
    "params",
    [
        ({"nhs_id_code": "foo"}),
        ({"nhs_mhs_svc_ia": "foo"}),
        ({"nhs_mhs_party_key": "foo"}),
        ({"bar": "foo", "foo": "bar"}),
    ],
)
def test_endpoint_query_invalid(params):
    with pytest.raises(ValidationError):
        search = SearchSDSEndpointQueryParams(**params)
