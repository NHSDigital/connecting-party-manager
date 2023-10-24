from uuid import UUID

import pytest
from domain.core.product_team import ProductTeam
from domain.core.root import Root
from domain.events.product_team_created_event import ProductTeamCreatedEvent


@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test__create_product_team(id: str, name: str):
    subject = Root.create_ods_organisation("AB123", "Test")
    user = Root.create_user("test@example.org", "Test User")

    (result, event) = subject.create_product_team(id, name, user)

    assert isinstance(result, ProductTeam), "Created ProductTeam"
    assert result.id == id, "id mismatch"
    assert result.name == name, "name mismatch"
    assert result.organisation == subject.as_reference(), "organisation mismatch"
    assert result.owner == user.as_reference(), "owner mismatch"

    assert isinstance(event, ProductTeamCreatedEvent), "Event type mismatch"
    assert event.id == id, "event id mismatch"
    assert event.id == id, "event id mismatch"
    assert event.name == name, "event name mismatch"
    assert event.organisation == subject.as_reference(), "event organisation mismatch"
    assert event.owner == user.as_reference(), "event owner mismatch"
