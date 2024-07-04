import pytest
from domain.core.device import Device, DeviceKeyType, DeviceType
from domain.core.device_key import DeviceKey
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository


@pytest.fixture
def device_with_asid() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    device.add_key(key="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(key="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    return device


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    device.add_key(key="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_mhs_id() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = team.create_device(name="Device-2", type=DeviceType.ENDPOINT)
    device.add_key(key="P.WWW-YYY", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key="ABC:DEF-444:4444444444", key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )
    return device


@pytest.mark.integration
def test__device_repository__add_two_keys(device: Device, repository: DeviceRepository):
    repository.write(device)
    second_device = repository.read_by_id(id=device.id)
    second_device.add_key(
        key="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID
    )
    repository.write(second_device)

    assert repository.read_by_id(id=device.id).keys == [
        DeviceKey(device_type=DeviceKeyType.PRODUCT_ID, key="P.WWW-XXX"),
        DeviceKey(device_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key="ABC:1234567890"),
    ]
    assert repository.read_by_key(key="P.WWW-XXX").keys == [
        DeviceKey(device_type=DeviceKeyType.PRODUCT_ID, key="P.WWW-XXX"),
        DeviceKey(device_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key="ABC:1234567890"),
    ]
    assert repository.read_by_key(key="ABC:1234567890").keys == [
        DeviceKey(device_type=DeviceKeyType.PRODUCT_ID, key="P.WWW-XXX"),
        DeviceKey(device_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key="ABC:1234567890"),
    ]


# @pytest.mark.integration
# def test__device_repository__test_big_data(repository: DeviceRepository):

#     org = Root.create_ods_organisation(ods_code="AB123")
#     product_team = org.create_product_team(
#         id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
#     )

#     devices = []
#     for i in range(1000000):
#         device = product_team.create_device(name=f"Device-{i}", type=DeviceType.PRODUCT)
#         device.add_key(key=f"ABC:{i}", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
#         delete_me = {
#             "complex": {
#                 "object": i
#             }
#         }

#         device.update(delete_me=delete_me)
#         devices.append(device.state())
#     repository.write_bulk(devices)


@pytest.mark.integration
def test__device_repository__delete_key(
    device_with_asid: Device, repository: DeviceRepository
):
    # Persist model before deleting from model
    repository.write(device_with_asid)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read_by_id(id=device_with_asid.id)

    intermediate_device.delete_key(key="ABC:1234567890")
    repository.write(intermediate_device)

    assert repository.read_by_id(id=device_with_asid.id).keys == [
        DeviceKey(device_type=DeviceKeyType.PRODUCT_ID, key="P.WWW-XXX")
    ]
