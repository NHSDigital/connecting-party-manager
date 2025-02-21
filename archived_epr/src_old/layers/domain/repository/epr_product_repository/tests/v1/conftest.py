from collections.abc import Generator

import pytest
from domain.core.root import Root
from domain.repository.device_repository.tests.utils import repository_fixture
from domain.repository.epr_product_repository import EprProductRepository


@pytest.fixture
def repository(request) -> Generator[EprProductRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=EprProductRepository,
    )


@pytest.fixture
def product():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team_epr(
        name="product-team-name",
        keys=[{"key_type": "product_team_id_alias", "key_value": "BAR"}],
    )
    return product_team.create_epr_product(name="epr-product-name")
