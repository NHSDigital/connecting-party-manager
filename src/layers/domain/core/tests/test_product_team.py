from unittest import mock
from uuid import UUID

import pytest
from domain.core.product import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root


@mock.patch("domain.core.product.validate_ods_code")
@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test__create_product_team(_mocked_validate_ods_code, id: str, name: str):
    org = Root.create_ods_organisation("AB123", "Test")
    user = Root.create_user("test@example.org", "Test User")

    (result, event) = org.create_product_team(id, name, user)

    assert isinstance(result, ProductTeam), "Created ProductTeam"
    assert result.id == id, "id mismatch"
    assert result.name == name, "name mismatch"
    assert result.organisation is org, "organisation mismatch"
    assert result.owner is user, "owner mismatch"

    assert isinstance(event, ProductTeamCreatedEvent), "Event type mismatch"
    assert event.product_team.id == id, "event id mismatch"
    assert event.product_team.name == name, "event name mismatch"
    assert event.product_team.organisation is org, "event organisation mismatch"
    assert event.product_team.owner is user, "event owner mismatch"
