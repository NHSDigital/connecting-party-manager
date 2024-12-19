import time

import pytest
from domain.core.device import Device
from domain.core.device_key import DeviceKey, DeviceKeyType
from domain.core.enum import Environment
from domain.repository.device_repository import DeviceRepository


@pytest.mark.integration
def test__device_repository__add_two_keys(device: Device, repository: DeviceRepository):
    repository.write(device)
    time.sleep(1)

    second_device = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        environment=Environment.DEV,
        id=device.id,
    )
    second_device.add_key(
        key_value="1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID
    )
    repository.write(second_device)
    time.sleep(1)

    assert repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        environment=Environment.DEV,
        id=device.id,
    ).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="1234567890"),
    ]
    assert repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        environment=Environment.DEV,
        id="P.WWW-XXX",
    ).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="1234567890"),
    ]
    assert repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        environment=Environment.DEV,
        id="1234567890",
    ).keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-XXX"),
        DeviceKey(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="1234567890"),
    ]


@pytest.mark.integration
def test__device_repository__delete_key(
    device_with_asid: Device, repository: DeviceRepository
):
    # Persist model before deleting from model
    repository.write(device_with_asid)
    time.sleep(1)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(
        product_team_id=device_with_asid.product_team_id,
        product_id=device_with_asid.product_id,
        environment=Environment.DEV,
        id=device_with_asid.id,
    )
    intermediate_device.delete_key(
        key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="1234567890"
    )
    repository.write(intermediate_device)
    time.sleep(1)

    assert repository.read(
        product_team_id=device_with_asid.product_team_id,
        product_id=device_with_asid.product_id,
        environment=Environment.DEV,
        id=device_with_asid.id,
    ).keys == [DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.WWW-CCC")]
