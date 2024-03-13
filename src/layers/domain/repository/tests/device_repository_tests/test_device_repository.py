import pytest
from domain.core.device import Device, DeviceKeyType, DeviceStatus, DeviceType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    device.add_key(key="P.WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.mark.integration
def test__device_repository(device: Device, repository: DeviceRepository):
    repository.write(device)
    assert repository.read(device.id) == device


@pytest.mark.integration
def test__device_repository_already_exists(device, repository: DeviceRepository):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(device)


@pytest.mark.integration
def test__device_repository__device_does_not_exist(repository: DeviceRepository):
    with pytest.raises(ItemNotFound):
        repository.read("123")


def test__device_repository_local(device: Device, repository: DeviceRepository):
    repository.write(device)
    assert repository.read(device.id) == device


def test__device_repository__device_does_not_exist_local(repository: DeviceRepository):
    with pytest.raises(ItemNotFound):
        repository.read("123")


@pytest.mark.integration
def test__device_repository__update(device: Device, repository: DeviceRepository):
    # Persist model before deleting from model
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(id=device.id)
    intermediate_device.update(name="foo-bar")
    repository.write(intermediate_device)

    final_device = repository.read(device.id)
    assert final_device.name == "foo-bar"


@pytest.mark.integration
def test__device_repository__delete(device: Device, repository: DeviceRepository):
    # Persist model before deleting from model
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(id=device.id)
    intermediate_device.delete()
    repository.write(intermediate_device)

    final_device = repository.read(device.id)
    assert final_device.status is DeviceStatus.INACTIVE
