from uuid import UUID

import pytest
from domain.core.product import Product, ProductStatus, ProductType


@pytest.mark.parametrize(
    ["id", "name", "ods_code", "ods_name", "product_team_id", "type", "status"],
    [
        [
            UUID("25b5f2a2-24e7-4460-b0e9-631a53bb66d3"),
            "Foo",
            "AB123",
            "AB123 Name",
            UUID("18934119-5780-4d28-b9be-0e6dff3908ba"),
            ProductType.SERVICE,
            ProductStatus.ACTIVE,
        ],
        [
            UUID("346edb01-cba3-4e89-b896-18f4489e9b59"),
            "Bah",
            "AB123",
            "AB123 Name",
            UUID("dcc11339-4ee1-4d24-a5e8-f66f2b367e5e"),
            ProductType.SERVICE,
            ProductStatus.ACTIVE,
        ],
        [
            UUID("fefeb8d2-0c4b-440d-891e-23dbd1f7df3e"),
            "Meep",
            "AB123",
            "AB123 Name",
            UUID("08dad8c7-a48d-49f9-8117-64fef37b9cfe"),
            ProductType.SERVICE,
            ProductStatus.ACTIVE,
        ],
    ],
)
def test__can_create_product(
    id: UUID,
    name: str,
    ods_code: str,
    ods_name: str,
    product_team_id: UUID,
    type: ProductType,
    status: ProductStatus,
):
    result = Product(
        id=id,
        name=name,
        ods_code=ods_code,
        ods_name=ods_name,
        product_team_id=product_team_id,
        type=type,
        status=status,
    )

    assert result is not None, "Result"
    assert result.id == id, "id"
    assert result.name == name, "name"
    assert result.ods_code == ods_code, "ods_code"
    assert result.ods_name == ods_name, "ods_name"
    assert result.product_team_id == product_team_id, "product_team_id"
