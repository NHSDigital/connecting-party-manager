import pytest
from domain.core.device.v2 import Device, DeviceType
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.device_key.v2 import DeviceKey
from domain.core.root.v2 import Root
from domain.repository.device_repository.v2 import DeviceRepository


@pytest.fixture
def device_with_asid() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", device_type=DeviceType.PRODUCT)
    device.add_key(key_value="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key_value="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID
    )
    return device


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", device_type=DeviceType.PRODUCT)
    device.add_key(key_value="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_mhs_id() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = team.create_device(name="Device-2", device_type=DeviceType.ENDPOINT)
    device.add_key(key_value="P.WWW-YYY", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key_value="ABC:DEF-444:4444444444",
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
    )
    return device


@pytest.mark.integration
def test__device_repository__add_two_keys(device: Device, repository: DeviceRepository):
    repository.write(device)
    second_device = repository.read(device.id)
    second_device.add_key(
        key_value="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID
    )
    repository.write(second_device)

    assert repository.read(device.id).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(
            key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="ABC:1234567890"
        ),
    ]
    assert repository.read(DeviceKeyType.PRODUCT_ID, "P.WWW-XXX").keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(
            key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="ABC:1234567890"
        ),
    ]
    assert repository.read(
        DeviceKeyType.ACCREDITED_SYSTEM_ID, "ABC:1234567890"
    ).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(
            key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="ABC:1234567890"
        ),
    ]


@pytest.mark.integration
def test__device_repository__delete_key(
    device_with_asid: Device, repository: DeviceRepository
):
    # Persist model before deleting from model
    repository.write(device_with_asid)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(device_with_asid.id)
    intermediate_device.delete_key(
        key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="ABC:1234567890"
    )
    repository.write(intermediate_device)

    assert repository.read(device_with_asid.id).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX")
    ]
