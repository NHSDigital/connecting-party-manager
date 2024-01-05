from uuid import UUID

import pytest
from domain.core.device import Device


@pytest.mark.parametrize(
    ["name", "ods_code", "product_team_id", "type", "status"],
    [
        [
            "Foo",
            "AB123",
            "18934119-5780-4d28-b9be-0e6dff3908ba",
            "product",
            "active",
        ]
    ],
)
def test__can_create_device(
    name: str,
    ods_code: str,
    product_team_id: str,
    type: str,
    status: str,
):
    device = Device(
        name=name,
        ods_code=ods_code,
        product_team_id=product_team_id,
        type=type,
        status=status,
    )
    assert isinstance(device.id, UUID)
    assert device.id.version == 4
    # Assert the existence of other attributes
    assert hasattr(device, "name")
    assert hasattr(device, "ods_code")
    assert hasattr(device, "product_team_id")
    assert hasattr(device, "type")
    assert hasattr(device, "status")

    # Assert that the values of the attributes are correct
    assert device.name == name
    assert device.ods_code == ods_code
    assert device.product_team_id == UUID(product_team_id)
    assert device.type == "product"
    assert device.status == "active"
