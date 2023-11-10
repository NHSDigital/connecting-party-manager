from uuid import UUID

import pytest
from domain.core.product import (
    ProductKeyType,
    ProductStatus,
    ProductType,
    RelationshipType,
)
from domain.core.root import Root
from repository.product_repo import ProductRepository

from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test__product_repository():
    subject_id = UUID("774c8c06-0d15-4b7d-9c7e-4a358681b78b")
    target_id = UUID("07bca737-1022-494c-8df0-5e7dd152ba59")
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123", name="Supplier")
    team = org.create_product_team(
        id=UUID("6f8c285e-04a2-4194-a84e-dabeba474ff7"), name="Team"
    )
    target = team.create_product(
        id=target_id,
        name="Target",
        type=ProductType.SERVICE,
        status=ProductStatus.ACTIVE,
    )
    subject = team.create_product(
        id=subject_id,
        name="Subject",
        type=ProductType.SERVICE,
        status=ProductStatus.ACTIVE,
    )
    subject.add_relationship(target, RelationshipType.DEPENDENCY)
    subject.add_key("XXX-YYY-ZZZ", ProductKeyType.PRODUCT_ID)
    subject.add_key("1234567890", ProductKeyType.ACCREDITED_SYSTEM_ID)

    product_repo = ProductRepository(table_name=table_name)

    product_repo.write(subject)

    result = product_repo.read(subject_id)

    assert result is not None, "result"
    assert result.id == subject.id, "id"
    assert result.name == subject.name, "name"
    assert result.ods_code == subject.ods_code, "ods_code"
    assert result.product_team_id == subject.product_team_id, "product_team_id"
    assert result.keys == subject.keys, "keys"
    assert result.relationships == subject.relationships, "relationships"
