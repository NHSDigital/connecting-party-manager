from uuid import UUID

import pytest
from domain.core.device import Device, DeviceStatus, DeviceType
from domain.core.error import InvalidKeyError
from domain.core.root import Root


@pytest.mark.parametrize(
    ["id", "name", "ods_code", "product_team_id", "type", "status"],
    [
        [
            UUID("25b5f2a2-24e7-4460-b0e9-631a53bb66d3"),
            "Foo",
            "AB123",
            UUID("18934119-5780-4d28-b9be-0e6dff3908ba"),
            DeviceType.SERVICE,
            DeviceStatus.ACTIVE,
        ],
        [
            UUID("346edb01-cba3-4e89-b896-18f4489e9b59"),
            "Bah",
            "AB123",
            UUID("dcc11339-4ee1-4d24-a5e8-f66f2b367e5e"),
            DeviceType.SERVICE,
            DeviceStatus.ACTIVE,
        ],
        [
            UUID("fefeb8d2-0c4b-440d-891e-23dbd1f7df3e"),
            "Meep",
            "AB123",
            UUID("08dad8c7-a48d-49f9-8117-64fef37b9cfe"),
            DeviceType.SERVICE,
            DeviceStatus.ACTIVE,
        ],
    ],
)
def test__can_create_device(
    id: UUID,
    name: str,
    ods_code: str,
    product_team_id: UUID,
    type: DeviceType,
    status: DeviceStatus,
):
    result = Device(
        id=id,
        name=name,
        ods_code=ods_code,
        product_team_id=product_team_id,
        type=type,
        status=status,
    )

    assert result is not None, "Result"
    assert result.id == id, "id"
    assert result.name == name, "name"
    assert result.ods_code == ods_code, "ods_code"
    assert result.product_team_id == product_team_id, "product_team_id"


@pytest.mark.parametrize("index", ["PROD", "env:PROD"])
def test__can_add_page(index: str):
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
    )
    subject = team.create_device(
        id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
        name="Product",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )

    result = subject.add_page(index)

    assert result is not None, "result"
    assert index in subject.pages, "pages"
    assert result.values is not None, "result.values"


@pytest.mark.parametrize("index", ["!!", "env:PROD:X"])
def test__cannot_add_page(index: str):
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
    )
    subject = team.create_device(
        id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
        name="Product",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )

    with pytest.raises(InvalidKeyError):
        subject.add_page(index)


@pytest.mark.parametrize("index", ["PROD", "env:PROD"])
def test__can_remove_page(index: str):
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
    )
    subject = team.create_device(
        id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
        name="Product",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_page(index)
    subject.remove_page(index)

    assert index not in subject.pages, "pages"
