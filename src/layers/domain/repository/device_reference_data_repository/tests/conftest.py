from collections.abc import Generator

import pytest
from domain.core.root.v3 import Root
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.tests.utils import repository_fixture


@pytest.fixture
def repository(request) -> Generator[DeviceReferenceDataRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=DeviceReferenceDataRepository,
    )


@pytest.fixture
def device_reference_data():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(name="product-team-name")
    product = product_team.create_cpm_product(name="product")
    return product.create_device_reference_data(name="device-reference-data")
