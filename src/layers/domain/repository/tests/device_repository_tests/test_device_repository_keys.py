import pytest
from domain.core.device import Device, DeviceKeyType, DeviceType
from domain.core.device_key import DeviceKey
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.marshall import unmarshall


@pytest.fixture
def device_with_asid() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", device_type=DeviceType.PRODUCT)
    device.add_key(key="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(key="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    return device


@pytest.fixture
def device_with_mhs_id() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = team.create_device(name="Device-2", device_type=DeviceType.ENDPOINT)
    device.add_key(key="P.WWW-YYY", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key="ABC:DEF-444:4444444444",
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
    )
    return device


@pytest.mark.integration
def test__device_repository__query_by_key_type(
    device_with_asid: Device, device_with_mhs_id: Device, repository: DeviceRepository
):
    repository.write(device_with_asid)
    repository.write(device_with_mhs_id)

    result = repository.query_by_key_type(
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_with_mhs_id.id)

    result = repository.query_by_key_type(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_with_asid.id)


@pytest.mark.integration
def test__device_repository__query_by_type(
    device_with_asid: Device, device_with_mhs_id: Device, repository: DeviceRepository
):
    repository.write(device_with_asid)
    repository.write(device_with_mhs_id)

    result = repository.query_by_device_type(device_type=DeviceType.ENDPOINT)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_with_mhs_id.id)

    result = repository.query_by_device_type(device_type=DeviceType.PRODUCT)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_with_asid.id)


@pytest.mark.integration
def test__device_repository__delete_key(
    device_with_asid: Device, repository: DeviceRepository
):
    # Persist model before deleting from model
    repository.write(device_with_asid)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(id=device_with_asid.id)
    intermediate_device.delete_key(key="ABC:1234567890")
    repository.write(intermediate_device)

    assert repository.read(device_with_asid.id).keys == {
        "P.WWW-XXX": DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key="P.WWW-XXX")
    }
