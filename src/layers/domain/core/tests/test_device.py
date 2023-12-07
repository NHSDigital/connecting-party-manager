from uuid import UUID

import pytest
from domain.core.device import Device


@pytest.mark.parametrize(
    ["id", "name", "ods_code", "product_team_id", "type", "status"],
    [
        [
            "25b5f2a2-24e7-4460-b0e9-631a53bb66d3",
            "Foo",
            "AB123",
            "18934119-5780-4d28-b9be-0e6dff3908ba",
            "service",
            "active",
        ],
        [
            "346edb01-cba3-4e89-b896-18f4489e9b59",
            "Bah",
            "AB123",
            "dcc11339-4ee1-4d24-a5e8-f66f2b367e5e",
            "service",
            "active",
        ],
        [
            "fefeb8d2-0c4b-440d-891e-23dbd1f7df3e",
            "Meep",
            "AB123",
            "08dad8c7-a48d-49f9-8117-64fef37b9cfe",
            "service",
            "active",
        ],
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
        "id": UUID(id),
        "name": name,
        "ods_code": ods_code,
        "product_team_id": UUID(product_team_id),
        "status": "active",
        "type": "service",
    }


# @pytest.mark.parametrize("index", ["PROD", "env:PROD"])
# def test__can_add_page(index: str):
#     org = Root.create_ods_organisation(ods_code="AB123")
#     team = org.create_product_team(
#         id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
#     )
#     subject = team.create_device(
#         id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
#         name="Product",
#         type=DeviceType.PRODUCT,
#         status=DeviceStatus.ACTIVE,
#     )

#     result = subject.add_page(index)

#     assert result is not None, "result"
#     assert index in subject.pages, "pages"
#     assert result.values is not None, "result.values"


# @pytest.mark.parametrize("index", ["!!", "env:PROD:X"])
# def test__cannot_add_page(index: str):
#     org = Root.create_ods_organisation(ods_code="AB123")
#     team = org.create_product_team(
#         id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
#     )
#     subject = team.create_device(
#         id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
#         name="Product",
#         type=DeviceType.PRODUCT,
#         status=DeviceStatus.ACTIVE,
#     )

#     with pytest.raises(InvalidKeyError):
#         subject.add_page(index)


# @pytest.mark.parametrize("index", ["PROD", "env:PROD"])
# def test__can_remove_page(index: str):
#     org = Root.create_ods_organisation(ods_code="AB123")
#     team = org.create_product_team(
#         id=UUID("f363c58b-1b6c-4fa6-a9b6-0c390808319b"), name="Team"
#     )
#     subject = team.create_device(
#         id=UUID("d4fa15c8-49f3-45f7-8143-43df21ca1438"),
#         name="Product",
#         type=DeviceType.PRODUCT,
#         status=DeviceStatus.ACTIVE,
#     )
#     subject.add_page(index)
#     subject.remove_page(index)

#     assert index not in subject.pages, "pages"
