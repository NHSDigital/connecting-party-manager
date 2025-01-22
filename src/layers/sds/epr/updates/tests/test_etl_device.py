import pytest
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.enum import Environment
from domain.core.root.v1 import Root
from sds.epr.updates.etl_device import DeviceHardDeletedEvent, EtlDevice


@pytest.fixture
def device():
    ods_org = Root.create_ods_organisation(ods_code="AAA")
    product_team = ods_org.create_product_team_epr(name="my product team")
    product = product_team.create_epr_product(name="my product")
    _device = product.create_device(name="my device", environment=Environment.PROD)
    _device.add_key(key_type=DeviceKeyType.CPA_ID, key_value="123456")
    _device.add_tag(foo="bar")
    _device.add_tag(foo="bar", bar="foo")
    _device.clear_events()
    return _device


def test_etl_device_copy_constructor(device: Device):
    etl_device = EtlDevice(**device.state())
    assert etl_device.state() == device.state()


def test_hard_delete(device: Device):
    etl_device = EtlDevice(**device.state())
    event = etl_device.hard_delete()
    assert etl_device.events == [event]

    assert event == DeviceHardDeletedEvent(
        id=str(device.id),
        keys=[{"key_type": "cpa_id", "key_value": "123456"}],
        tags=["bar=foo&foo=bar", "foo=bar"],
    )
