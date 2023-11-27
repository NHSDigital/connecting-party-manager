from uuid import UUID

import pytest
from domain.core.product_team import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root
from pydantic import ValidationError


@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test__create_product_team(id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123", name="Test")

    result = org.create_product_team(id=id, name=name)
    event = result.events[0]

    assert isinstance(result, ProductTeam), "Created ProductTeam"
    assert result.id == id, "id mismatch"
    assert result.name == name, "name mismatch"
    assert result.ods_code == org.ods_code, "ods_code"

    assert len(result.events) == 1
    event = result.events[0]
    assert isinstance(event, ProductTeamCreatedEvent), "Event type mismatch"
    assert event.id == id, "id mismatch"
    assert event.name == name, "name mismatch"
    assert result.ods_code == org.ods_code, "organisation.id mismatch"


@pytest.mark.parametrize(
    "id,name",
    [
        ["123", "First"],
        ["  ", "Second"],
    ],
)
def test__create_product_team_bad_id(id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123", name="Test")

    with pytest.raises(ValidationError):
        org.create_product_team(id=id, name=name)


@pytest.mark.parametrize(
    "id,name",
    [
        ["ae28e872-843d-4e2e-9f0b-b5d3c42d441f", " "],
    ],
)
def test__create_product_team_bad_name(id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123", name="Test")

    with pytest.raises(ValidationError):
        org.create_product_team(id=id, name=name)
