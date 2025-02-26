from typing import Generator

import pytest
from domain.core.device import Device
from domain.core.device_key import DeviceKeyType
from domain.core.enum import Environment
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.device_repository.tests.utils import repository_fixture


@pytest.fixture
def repository(request) -> Generator[DeviceRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=DeviceRepository,
    )


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team_epr(name="Team")
    product = product_team.create_epr_product(name="Product")
    device = product.create_device(name="Device-1", environment=Environment.DEV)
    device.add_tag(abc="123")
    device.add_tag(bar="foo")
    device.add_tag(mixed_case="AbC")
    device.add_key(key_value="P.WWW-XXX", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_asid() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team_epr(name="Team")
    product = product_team.create_epr_product(name="Product")
    device = product.create_device(name="Device-1", environment=Environment.DEV)
    device.add_tag(foo="bar", abc="123")
    device.add_tag(bar="foo")
    device.add_key(key_value="1234567890", key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    device.add_key(key_value="P.WWW-CCC", key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_mhs_id() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team_epr(name="Team")
    product = product_team.create_epr_product(name="Product")
    device = product.create_device(name="Device-2", environment=Environment.DEV)
    device.add_key(key_value="P.WWW-YYY", key_type=DeviceKeyType.PRODUCT_ID)
    device.add_key(
        key_value="123456",
        key_type=DeviceKeyType.CPA_ID,
    )
    device.add_tag(abc="123")
    device.add_tag(bar="foo")
    return device
