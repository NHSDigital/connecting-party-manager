from copy import deepcopy

import pytest
from domain.core.device import (
    Device,
    DeviceKeyAddedEvent,
    DeviceKeyType,
    DeviceStatus,
    DeviceType,
)
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound

DEVICE_KEY = "P.WWW-XXX"


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    device.add_key(key=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_no_key() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    return device


@pytest.mark.integration
def test__device_repository_read_by_id(device: Device, repository: DeviceRepository):
    repository.write(device)
    assert repository.read_by_id(id=device.id) == device


@pytest.mark.integration
def test__device_repository_read_by_key(device: Device, repository: DeviceRepository):
    repository.write(device)
    assert repository.read_by_id(id=DEVICE_KEY) == device


@pytest.mark.integration
def test__device_repository_already_exists(device, repository: DeviceRepository):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(device)


@pytest.mark.integration
def test__device_repository__device_does_not_exist(repository: DeviceRepository):
    with pytest.raises(ItemNotFound):
        repository.read_by_id(id="123")


def test__device_repository_local(device: Device, repository: DeviceRepository):
    repository.write(device)
    assert repository.read_by_id(id=device.id) == device


def test__device_repository__device_does_not_exist_local(repository: DeviceRepository):
    with pytest.raises(ItemNotFound):
        repository.read_by_id(id="123")


@pytest.mark.integration
def test__device_repository__update(device: Device, repository: DeviceRepository):
    # Persist model before deleting from model
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read_by_id(id=device.id)
    intermediate_device.update(name="foo-bar")
    repository.write(intermediate_device)

    final_device = repository.read_by_id(id=device.id)
    assert final_device.name == "foo-bar"


@pytest.mark.integration
def test__device_repository__delete(device: Device, repository: DeviceRepository):
    # Persist model before deleting from model
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read_by_id(id=device.id)
    intermediate_device.delete()
    repository.write(intermediate_device)

    final_device = repository.read_by_id(id=device.id)
    assert final_device.status is DeviceStatus.INACTIVE


@pytest.mark.integration
def test__device_repository__existing_keys_and_update(
    device_no_key: Device, repository: DeviceRepository
):
    repository.write(device_no_key)
    add_key_event = DeviceKeyAddedEvent(
        id=device_no_key.id, key=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID
    )

    (
        existing_device_keys,
        updated_device,
    ) = repository._get_existing_keys_and_update_device_with_new_key(add_key_event)

    assert existing_device_keys == {}
    device_with_key = deepcopy(device_no_key.dict())
    expected_device_keys = {"P.WWW-XXX": DeviceKeyType.PRODUCT_ID}
    device_with_key["keys"] = expected_device_keys

    assert updated_device == device_with_key


@pytest.mark.integration
def test__device_repository__batch_get_items_one_key(
    device: Device, repository: DeviceRepository
):
    repository.write(device)
    data_device = repository.read_by_id(id=device.id)

    results = repository._batch_get_items(id=device.id, keys=data_device.keys)
    expected_device_keys = {"P.WWW-XXX": DeviceKeyType.PRODUCT_ID}

    number_of_devices = []
    for device in results:
        assert device["keys"] == expected_device_keys
        number_of_devices.append(device)

    assert len(number_of_devices) == 3
