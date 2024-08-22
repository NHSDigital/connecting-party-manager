from uuid import UUID

import pytest
from domain.core.product_team.v1 import ProductTeam as ProductTeamV1
from domain.core.product_team.v1 import (
    ProductTeamCreatedEvent as ProductTeamCreatedEventV1,
)
from domain.core.product_team.v2 import ProductTeam as ProductTeamV2
from domain.core.product_team.v2 import (
    ProductTeamCreatedEvent as ProductTeamCreatedEventV2,
)
from domain.core.root.v1 import Root as RootV1
from domain.core.root.v2 import Root as RootV2
from pydantic import ValidationError


@pytest.mark.parametrize(
    ["ProductTeam", "ProductTeamCreatedEvent", "Root"],
    (
        [ProductTeamV1, ProductTeamCreatedEventV1, RootV1],
        [ProductTeamV2, ProductTeamCreatedEventV2, RootV2],
    ),
)
@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test__create_product_team(
    ProductTeam: type[ProductTeamV2],
    ProductTeamCreatedEvent: type[ProductTeamCreatedEventV2],
    Root: type[RootV2],
    id: str,
    name: str,
):
    org = Root.create_ods_organisation(ods_code="AB123")

    result = org.create_product_team(id=str(id), name=name)
    event = result.events[0]

    assert isinstance(result, ProductTeam)
    assert result.id == id
    assert result.name == name
    assert result.ods_code == org.ods_code

    assert len(result.events) == 1
    assert isinstance(event, ProductTeamCreatedEvent)
    assert event.id == id
    assert event.name == name
    assert event.ods_code == org.ods_code


@pytest.mark.parametrize("Root", (RootV1, RootV2))
@pytest.mark.parametrize(
    "id,name",
    [
        ["123", "First"],
        ["  ", "Second"],
    ],
)
def test__create_product_team_bad_id(Root: type[RootV2], id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123")

    with pytest.raises(ValidationError):
        org.create_product_team(id=id, name=name)


@pytest.mark.parametrize("Root", (RootV1, RootV2))
@pytest.mark.parametrize(
    "id,name",
    [
        ["ae28e872-843d-4e2e-9f0b-b5d3c42d441f", " "],
    ],
)
def test__create_product_team_bad_name(Root: type[RootV2], id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123")

    with pytest.raises(ValidationError):
        org.create_product_team(id=id, name=name)
