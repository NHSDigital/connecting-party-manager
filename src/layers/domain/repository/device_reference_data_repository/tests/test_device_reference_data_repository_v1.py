import pytest
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.repository.device_reference_data_repository.v1 import (
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
        device_reference_data_id=device_reference_data.id,
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
            device_reference_data_id=device_reference_data_id,
        )


def test__cpm_product_repository_local(
    device_reference_data: DeviceReferenceData,
    repository: DeviceReferenceDataRepository,
):
    repository.write(device_reference_data)
    result = repository.read(
        product_team_id=device_reference_data.product_team_id,
        product_id=device_reference_data.product_id,
        device_reference_data_id=device_reference_data.id,
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
            device_reference_data_id=device_reference_data_id,
        )
