from typing import Generator

import pytest
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.device_repository.tests.utils import repository_fixture


@pytest.fixture
def repository(request) -> Generator[CpmProductRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=CpmProductRepository,
    )


@pytest.fixture
def product():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        name="product-team-name",
        keys=[{"key_type": "product_team_id_alias", "key_value": "BAR"}],
    )
    return product_team.create_cpm_product(name="cpm-product-name")
