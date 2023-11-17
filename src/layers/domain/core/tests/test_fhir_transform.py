from unittest import mock
from uuid import UUID

import pytest
from domain.core.constants import REQUIRED_CREATE_FIELDS
from domain.core.fhir_transform import (
    create_fhir_model_from_fhir_json,
    create_fhir_model_from_product_team,
    create_product_team_from_fhir_json,
)
from domain.core.product import OdsOrganisation, ProductTeam
from domain.core.root import Root
from domain.core.tests.utils import read_test_data
from domain.core.user import User
from domain.fhir.r4.cpm_model import Organization
from domain.fhir.r4.strict_models import Organization as StrictOrganization
from pydantic import ValidationError


@pytest.mark.parametrize(
    "fhir_type, fhir_name, model_type, json_file",
    [
        (
            StrictOrganization,
            "Organization",
            Organization,
            "organization-fhir-example-required.json",
        )
    ],
)
def test_null_values_raise_error(fhir_type, fhir_name, model_type, json_file):
    fhir_json = read_test_data(json_file)
    for key in REQUIRED_CREATE_FIELDS[fhir_name]:
        if isinstance(fhir_json[key], list):
            pass
            fhir_json[key] = []
        elif isinstance(fhir_json[key], dict):
            pass
            fhir_json[key] = {}
        else:
            fhir_json[key] = ""
    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(fhir_json, [fhir_type], model_type)


@pytest.mark.parametrize(
    "fhir_type, model_type, json_file",
    [(StrictOrganization, Organization, "organization-fhir-example-full.json")],
)
def test_validate_no_extra_fields(fhir_type, model_type, json_file):
    fhir_json = read_test_data(json_file)
    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(fhir_json, [fhir_type], model_type)


@pytest.mark.parametrize(
    "fhir_type, fhir_name, model_type, json_file",
    [
        (
            StrictOrganization,
            "Organization",
            Organization,
            "organization-fhir-example-required.json",
        )
    ],
)
def test_validate_required_create_fields(fhir_type, fhir_name, model_type, json_file):
    fhir_json = read_test_data(json_file)
    for key in REQUIRED_CREATE_FIELDS[fhir_name]:
        fhir_json.pop(key)

    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(fhir_json, [fhir_type], model_type)


def test_email_validates_organization():
    fhir_json = read_test_data("organization-fhir-example-required.json")
    fhir_json["contact"][0]["telecom"][0]["value"] = "foobar"
    with pytest.raises(ValidationError):
        create_fhir_model_from_fhir_json(fhir_json, [StrictOrganization], Organization)


@pytest.mark.parametrize(
    "expected_fields, expected_values, json_file",
    [
        (
            ["id", "name", "organisation", "owner"],
            ["f9518c12-6c83-4544-97db-d9dd1d64da97", "Test-Organization"],
            "organization-fhir-example-required.json",
        )
    ],
)
def test_create_product_team_from_fhir_organization(
    expected_fields, expected_values, json_file
):
    fhir_json = read_test_data(json_file)
    core_model = create_product_team_from_fhir_json(fhir_json=fhir_json)

    assert isinstance(core_model, ProductTeam)
    for key, field in enumerate(expected_fields):
        assert hasattr(core_model, field)
        if field == "organisation":
            assert isinstance(core_model.organisation, OdsOrganisation)
        elif field == "owner":
            assert isinstance(core_model.owner, User)
        else:
            assert getattr(core_model, field) == expected_values[key]


@mock.patch("domain.core.product.validate_ods_code")
@pytest.mark.parametrize(
    "id,name",
    [
        [UUID("ae28e872-843d-4e2e-9f0b-b5d3c42d441f"), "First"],
        [UUID("edf90c3a-f865-4dd9-9ab9-400e6ebc02e0"), "Second"],
        [UUID("f9518c12-6c83-4544-97db-d9dd1d64da97"), "Third"],
    ],
)
def test_product_team_to_fhir_organization(
    _mocked_validate_ods_code, id: str, name: str
):
    org = Root.create_ods_organisation("AB123", "Test")
    user = Root.create_user("test@example.org", "Test User")

    (result, event) = org.create_product_team(id, name, user)
    fhir_model = create_fhir_model_from_product_team(result)
    assert isinstance(fhir_model, Organization)
