import pytest
from domain.core.device.v2 import Device, DeviceTag
from domain.core.device_key.v2 import DeviceKeyType
from domain.repository.device_repository.v2 import DeviceRepository


@pytest.mark.integration
def test__device_repository__tags(device: Device, repository: DeviceRepository):
    repository.write(device)
    (_device_123,) = repository.query_by_tag(abc=123)
    assert _device_123.dict() == device.dict()

    (_device_bar,) = repository.query_by_tag(bar="foo")
    assert _device_bar.dict() == device.dict()


@pytest.mark.integration
def test__device_repository__tag_does_not_exist(
    device: Device, repository: DeviceRepository
):
    repository.write(device)
    results = repository.query_by_tag(abc=12)
    assert len(results) == 0


@pytest.mark.integration
def test__device_repository__multiple_devices_with_same_tags(
    device: Device,
    device_with_asid: Device,
    device_with_mhs_id: Device,
    repository: DeviceRepository,
):
    repository.write(device)
    repository.write(device_with_asid)
    repository.write(device_with_mhs_id)

    devices = repository.query_by_tag(bar="foo")
    assert len(devices) == 3

    assert devices == sorted(
        (device, device_with_asid, device_with_mhs_id), key=lambda d: d.id
    )


@pytest.mark.integration
def test__device_repository__add_two_tags(device: Device, repository: DeviceRepository):
    repository.write(device)
    second_device = repository.read(device.id)
    second_device.add_tag(shoe_size=123)
    second_device.add_tag(shoe_size=456)
    repository.write(second_device)

    expected_tags = [
        DeviceTag(components=[("abc", "123")]),
        DeviceTag(components=[("bar", "foo")]),
        DeviceTag(components=[("shoe_size", "123")]),
        DeviceTag(components=[("shoe_size", "456")]),
    ]

    assert repository.read(device.id).tags == expected_tags
    assert repository.read(DeviceKeyType.PRODUCT_ID, "P.WWW-XXX").tags == expected_tags

    (_device_123,) = repository.query_by_tag(shoe_size=123)
    assert _device_123.dict() == second_device.dict()

    (_device_456,) = repository.query_by_tag(shoe_size=456)
    assert _device_456.dict() == second_device.dict()
