import pytest
from domain.core.device.v2 import Device
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.device_key.v2 import DeviceKey
from domain.repository.device_repository.v2 import DeviceRepository


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
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-CCC")
    ]
