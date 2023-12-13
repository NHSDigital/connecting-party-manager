from uuid import UUID

import pytest
from domain.core.device import Device


@pytest.mark.parametrize(
    ["id", "name", "ods_code", "product_team_id", "type", "status"],
    [
        [
            "XXX-YYY",
            "Foo",
            "AB123",
            "18934119-5780-4d28-b9be-0e6dff3908ba",
            "product",
            "active",
        ]
    ],
)
def test__can_create_device(
    id: str,
    name: str,
    ods_code: str,
    product_team_id: str,
    type: str,
    status: str,
):
    device = Device(
        id=id,
        name=name,
        ods_code=ods_code,
        product_team_id=product_team_id,
        type=type,
        status=status,
    )
    assert device.dict() == {
        "id": id,
        "name": name,
        "ods_code": ods_code,
        "product_team_id": UUID(product_team_id),
        "status": "active",
        "type": "product",
    }
