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

    for value in ["aBc", "ABC", "abc", "AbC"]:
        (_device_abc,) = repository.query_by_tag(mixed_case=value)
        assert _device_abc.dict() == device.dict()


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


def _test_add_two_tags(
    device: Device, second_device: Device, repository: DeviceRepository
):
    expected_tags = {
        DeviceTag(abc="123"),
        DeviceTag(bar="foo"),
        DeviceTag(mixed_case="abc"),
        DeviceTag(shoe_size="123"),
        DeviceTag(shoe_size="456"),
    }

    assert repository.read(device.id).tags == expected_tags
    assert repository.read(DeviceKeyType.PRODUCT_ID, "P.WWW-XXX").tags == expected_tags

    (_device_123,) = repository.query_by_tag(shoe_size=123)
    assert _device_123.dict() == second_device.dict()

    (_device_456,) = repository.query_by_tag(shoe_size=456)
    assert _device_456.dict() == second_device.dict()
    return True


@pytest.mark.integration
def test__device_repository__add_two_tags(device: Device, repository: DeviceRepository):
    repository.write(device)
    second_device = repository.read(device.id)
    second_device.add_tag(shoe_size=123)
    second_device.add_tag(shoe_size=456)
    repository.write(second_device)

    assert _test_add_two_tags(
        device=device, second_device=second_device, repository=repository
    )


@pytest.mark.integration
def test__device_repository__add_two_tags_at_once(
    device: Device, repository: DeviceRepository
):
    repository.write(device)
    second_device = repository.read(device.id)
    second_device.add_tags([dict(shoe_size=123), dict(shoe_size=456)])
    repository.write(second_device)

    assert _test_add_two_tags(
        device=device, second_device=second_device, repository=repository
    )


@pytest.mark.integration
def test__device_repository__add_two_tags_and_then_clear(
    device: Device, repository: DeviceRepository
):
    repository.write(device)
    second_device = repository.read(device.id)
    second_device.add_tags([dict(shoe_size=123), dict(shoe_size=456)])
    repository.write(second_device)

    second_device.clear_events()
    second_device.clear_tags()
    repository.write(second_device)

    assert repository.read(device.id).tags == set()
    assert repository.read(DeviceKeyType.PRODUCT_ID, "P.WWW-XXX").tags == set()

    assert repository.query_by_tag(shoe_size=123) == []
    assert repository.query_by_tag(shoe_size=456) == []
