from typing import Generator

import pytest
from domain.core.device.v3 import Device
from domain.core.device_key.v2 import DeviceKeyType
from domain.core.root.v3 import Root
from domain.repository.device_repository.tests.utils import repository_fixture
from domain.repository.device_repository.v3 import DeviceRepository


@pytest.fixture
def repository(request) -> Generator[DeviceRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=DeviceRepository,
    )


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-1")
    device.add_tag(abc="123")
    device.add_tag(bar="foo")
    device.add_tag(mixed_case="AbC")
    device.add_key(key_value="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_asid() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-1")
    device.add_tag(foo="bar", abc="123")
    device.add_tag(bar="foo")
    device.add_key(
        key_value="ABC:1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID
    )
    device.add_key(key_value="P.WWW-CCC", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_mhs_id() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-2")
    device.add_key(key_value="P.WWW-YYY", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key_value="ABC:DEF-444:4444444444",
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
    )
    device.add_tag(abc="123")
    device.add_tag(bar="foo")
    return device