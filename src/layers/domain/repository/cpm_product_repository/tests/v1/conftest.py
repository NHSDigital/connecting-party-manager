from collections.abc import Generator

import pytest
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.cpm_product_repository.tests.utils import repository_fixture_cpm


@pytest.fixture
def repository(request) -> Generator[CpmProductRepository, None, None]:
    yield from repository_fixture_cpm(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=CpmProductRepository,
    )


@pytest.fixture
def product():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        name="product-team-name",
        keys=[
            {
                "key_type": "product_team_id",
                "key_value": "808a36db-a52a-4130-b71e-d9cbcbaed15b",
            }
        ],
    )
    return product_team.create_cpm_product(name="cpm-product-name")
