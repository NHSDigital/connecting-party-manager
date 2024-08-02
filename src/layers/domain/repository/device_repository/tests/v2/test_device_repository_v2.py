import pytest
from domain.core.device.v2 import Device as DeviceV2
from domain.core.device.v2 import DeviceType as DeviceTypeV2
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.device_key.v2 import DeviceKey as DeviceKeyV2
from domain.core.enum import Status
from domain.core.root.v2 import Root
from domain.repository.device_repository.v2 import (
    DeviceRepository as DeviceRepositoryV2,
)
from domain.repository.device_repository.v2 import _device_primary_keys
from domain.repository.errors import AlreadyExistsError, ItemNotFound

DEVICE_KEY = "P.WWW-XXX"


@pytest.fixture
def device() -> DeviceV2:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(
        name="Device-1", device_type=DeviceTypeV2.PRODUCT
    )
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def another_device_with_same_key() -> DeviceV2:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(
        name="Device-2", device_type=DeviceTypeV2.PRODUCT
    )
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    return device


def test__device_primary_keys():
    primary_keys = _device_primary_keys(
        device_id="123",
        device_keys=[
            DeviceKeyV2(key_type=DeviceKeyType.PRODUCT_ID, key_value=DEVICE_KEY)
        ],
    )
    assert primary_keys == [
        {"pk": {"S": "D#123"}, "sk": {"S": "D#123"}},
        {
            "pk": {"S": f"D#product_id#P.WWW-XXX"},
            "sk": {"S": f"D#product_id#P.WWW-XXX"},
        },
    ]


@pytest.mark.integration
def test__device_repository_read_by_id(
    device: DeviceV2, repository: DeviceRepositoryV2
):
    repository.write(device)
    device_from_db = repository.read(device.id)
    assert device_from_db.dict() == device.dict()


@pytest.mark.integration
def test__device_repository_read_by_key(
    device: DeviceV2, repository: DeviceRepositoryV2
):
    repository.write(device)
    device_from_db = repository.read(*device.keys[0].parts)
    assert device_from_db.dict() == device.dict()


@pytest.mark.integration
def test__device_repository_already_exists(device, repository: DeviceRepositoryV2):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(device)


@pytest.mark.integration
def test__device_repository_key_already_exists_on_another_device(
    device, another_device_with_same_key, repository: DeviceRepositoryV2
):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(another_device_with_same_key)


def test__device_repository_key_already_exists_on_another_device(
    device, another_device_with_same_key, repository: DeviceRepositoryV2
):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(another_device_with_same_key)


@pytest.mark.integration
def test__device_repository__device_does_not_exist(repository: DeviceRepositoryV2):
    with pytest.raises(ItemNotFound):
        repository.read("123")


def test__device_repository_local(device: DeviceV2, repository: DeviceRepositoryV2):
    repository.write(device)
    device_from_db = repository.read(device.id)
    assert device_from_db.dict() == device.dict()


def test__device_repository__device_does_not_exist_local(
    repository: DeviceRepositoryV2,
):
    with pytest.raises(ItemNotFound):
        repository.read("123")


@pytest.mark.integration
def test__device_repository__update(device: DeviceV2, repository: DeviceRepositoryV2):
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(device.id)
    intermediate_device.update(name="foo-bar")
    repository.write(intermediate_device)

    final_device = repository.read(device.id)
    assert final_device.name == "foo-bar"


@pytest.mark.integration
def test__device_repository__delete(device: DeviceV2, repository: DeviceRepositoryV2):
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(device.id)
    intermediate_device.delete()
    repository.write(intermediate_device)

    final_device = repository.read(device.id)
    assert final_device.status is Status.INACTIVE


@pytest.mark.integration
def test__device_repository__add_key(device: DeviceV2, repository: DeviceRepositoryV2):
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(device.id)
    assert len(intermediate_device.keys) == 1

    intermediate_device.add_key(
        key_type=DeviceKeyType.PRODUCT_ID, key_value="P.AAA-CCC"
    )
    repository.write(intermediate_device)

    retrieved_devices = []
    for key_parts in [(intermediate_device.id,)] + [
        k.parts for k in intermediate_device.keys
    ]:
        _device = repository.read(*key_parts).dict()
        retrieved_devices.append(_device)

    # Assert that there are 2 keys, the device can be retrieved 3 ways from the db,
    # and that all 3 are identical
    assert len(intermediate_device.keys) == 2
    assert len(retrieved_devices) == 3
    assert [retrieved_devices[0]] * 3 == retrieved_devices
