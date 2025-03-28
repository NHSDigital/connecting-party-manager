import pytest
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.errors import AlreadyExistsError, ItemNotFound

from test_helpers.uuid import consistent_uuid


@pytest.mark.integration
def test__cpm_device_reference_data_repository(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    result = repository.read(
        product_team_id=device_reference_data.product_team_id,
        product_id=device_reference_data.product_id,
        environment=Environment.DEV,
        id=device_reference_data.id,
    )
    assert result == device_reference_data


@pytest.mark.integration
def test__cpm_device_reference_data_repository_already_exists(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    with pytest.raises(AlreadyExistsError):
        repository.write(device_reference_data)


@pytest.mark.integration
def test__cpm_device_reference_data_repository__device_reference_data_does_not_exist(
    repository: DeviceReferenceDataRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    device_reference_data_id = consistent_uuid(2)
    with pytest.raises(ItemNotFound):
        repository.read(
            product_team_id=product_team_id,
            product_id=product_id,
            environment=Environment.DEV,
            id=device_reference_data_id,
        )


def test__epr_product_repository_local(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    result = repository.read(
        product_team_id=device_reference_data.product_team_id,
        product_id=device_reference_data.product_id,
        environment=Environment.DEV,
        id=device_reference_data.id,
    )
    assert result == device_reference_data


def test__cpm_device_reference_data_repository__device_reference_data_does_not_exist_local(
    repository: DeviceReferenceDataRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    device_reference_data_id = consistent_uuid(2)
    with pytest.raises(ItemNotFound):
        repository.read(
            product_team_id=product_team_id,
            product_id=product_id,
            environment=Environment.DEV,
            id=device_reference_data_id,
        )


@pytest.mark.integration
def test__cpm_device_reference_data_repository__search_empty(
    repository: DeviceReferenceDataRepository,
):
    results = repository.search(
        product_team_id="foo", product_id="bar", environment=Environment.DEV
    )
    assert results == []


def test__cpm_device_reference_data_repository__search_empty_local(
    repository: DeviceReferenceDataRepository,
):
    results = repository.search(
        product_team_id="foo", product_id="bar", environment=Environment.DEV
    )
    assert results == []


@pytest.mark.integration
def test__cpm_device_reference_data_repository__search_not_empty(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    results = repository.search(
        product_team_id=device_reference_data.product_team_id,
        product_id=device_reference_data.product_id,
        environment=Environment.DEV,
    )
    assert results == [device_reference_data]


def test__cpm_device_reference_data_repository__search_not_empty_local(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    results = repository.search(
        product_team_id=device_reference_data.product_team_id,
        product_id=device_reference_data.product_id,
        environment=Environment.DEV,
    )
    assert results == [device_reference_data]
