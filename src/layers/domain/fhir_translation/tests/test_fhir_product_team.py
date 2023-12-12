from uuid import UUID

import pytest
from domain.core.product_team import ProductTeam
from domain.core.root import Root
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir.r4.models import Organization
from domain.fhir.r4.strict_models import Organization as StrictOrganization
from domain.fhir_translation.product_team import (
    create_fhir_model_from_fhir_json,
    create_fhir_model_from_product_team,
    create_product_team_from_fhir_org_json,
)
from domain.fhir_translation.tests.utils import read_test_data
from pydantic import ValidationError

REQUIRED_CREATE_FIELDS = {
    "Organization": ["resourceType", "identifier", "name", "partOf"]
}


def test_null_values_raise_error():
    fhir_json = read_test_data("organization-fhir-example-required.json")
    for key in REQUIRED_CREATE_FIELDS[Organization.__name__]:
        item_type = type(fhir_json[key])
        fhir_json[key] = item_type()
    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(
            fhir_json=fhir_json,
            fhir_models=[Organization, StrictOrganization],
            our_model=ProductTeamOrganization,
        )


def test_validate_no_extra_fields():
    fhir_json = read_test_data("organization-fhir-example-full.json")
    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(
            fhir_json=fhir_json,
            fhir_models=[StrictOrganization, Organization],
            our_model=ProductTeamOrganization,
        )


def test_validate_required_create_fields():
    fhir_json = read_test_data("organization-fhir-example-required.json")
    for key in REQUIRED_CREATE_FIELDS[Organization.__name__]:
        fhir_json.pop(key)

    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(
            fhir_json=fhir_json,
            fhir_models=[StrictOrganization, Organization],
            our_model=ProductTeamOrganization,
        )


@pytest.mark.parametrize(
    "expected_fields, expected_values",
    [
        (
            ["id", "name"],
            ["f9518c12-6c83-4544-97db-d9dd1d64da97", "Test-Organization"],
        )
    ],
)
def test_create_product_team_from_fhir_organization(expected_fields, expected_values):
    fhir_json = read_test_data("organization-fhir-example-required.json")
    core_model = create_product_team_from_fhir_org_json(fhir_org_json=fhir_json)

    assert isinstance(core_model, ProductTeam)
    for key, field in enumerate(expected_fields):
        assert hasattr(
            core_model, field
        ), f"{field} missing from {core_model.__class__.__name__}"
        assert str(getattr(core_model, field)) == str(expected_values[key])


@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test_product_team_to_fhir_organization(id: str, name: str):
    org = Root.create_ods_organisation(ods_code="AB123")

    result = org.create_product_team(id=id, name=name)
    fhir_model = create_fhir_model_from_product_team(result)
    assert isinstance(fhir_model, ProductTeamOrganization)
