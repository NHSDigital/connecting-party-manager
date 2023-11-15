import json
from unittest import mock
from uuid import UUID

import pytest
from domain.core.constants import EMPTY_VALUES, REQUIRED_CREATE_FIELDS
from domain.core.error import (
    BadEmailFieldError,
    FhirValidationError,
    MissingRequiredFieldForCreate,
)
from domain.core.fhir_transform import (
    create_fhir_model_from_product_team,
    create_product_team_from_fhir_json,
    strip_empty_json_paths,
    validate_contact_details,
    validate_no_extra_fields,
    validate_required_create_fields,
)
from domain.core.product import OdsOrganisation, ProductTeam
from domain.core.root import Root
from domain.core.tests.utils import read_test_data
from domain.core.user import User
from domain.fhir.r4.strict_models import Organization as StrictOrganization
from pydantic import BaseModel

NULLISH_VALUES = ["null", "[]", "{}", '""']


def test_nullish_fields_consistent_with_empty_values():
    assert sorted(NULLISH_VALUES) == sorted(map(json.dumps, EMPTY_VALUES))


@pytest.mark.parametrize(
    "bad_json",
    (
        {"foo": {"bar": [None]}, "oof": "rab"},
        {"foo": {"bar": []}, "oof": "rab"},
        {"foo": {}, "oof": "rab"},
    ),
)
def test_strip_empty_json_paths(bad_json):
    # Confirm bad fields are present
    bad_json_str = json.dumps(bad_json)
    assert any(nullish_field in bad_json_str for nullish_field in NULLISH_VALUES)

    stripped_bad_json = strip_empty_json_paths(bad_json)
    assert stripped_bad_json == {"oof": "rab"}

    # Confirm bad fields are gone
    stripped_bad_json_str = json.dumps(stripped_bad_json)
    assert not any(
        nullish_field in stripped_bad_json_str for nullish_field in NULLISH_VALUES
    )


@pytest.mark.parametrize(
    "bad_json",
    (
        {"foo": {"bar": [None]}, "oof": "rab"},
        {"foo": {"bar": []}, "oof": "rab"},
        {"foo": {}, "oof": "rab"},
    ),
)
def test_strip_empty_json_paths(bad_json):
    with pytest.raises(FhirValidationError):
        strip_empty_json_paths(bad_json, True)


def test_strip_empty_json_paths_throws_error_when_field_missing():
    assert REQUIRED_CREATE_FIELDS["Organization"] == [
        "identifier",
        "name",
        "partOf",
        "contact",
    ]


class Foo(BaseModel):
    spam: str
    eggs: int


def test_validate_no_extra_fields_success():
    json_without_extra_fields = {"spam": "SPAM", "eggs": 123}
    json_as_model = Foo(**json_without_extra_fields)
    validate_no_extra_fields(
        json_as_model.dict(exclude_none=True), json_without_extra_fields
    )


def test_validate_no_extra_fields_failure():
    json_with_extra_fields = {"spam": "SPAM", "eggs": 123, "bar": "BAR"}
    json_as_model = Foo(**json_with_extra_fields)
    with pytest.raises(FhirValidationError):
        validate_no_extra_fields(
            json_as_model.dict(exclude_none=True), json_with_extra_fields
        )


@pytest.mark.parametrize(
    "model_type, json_file", [("Organization", "organization-fhir-example.json")]
)
def test_validate_required_create_fields(model_type, json_file):
    fhir_json = read_test_data(json_file)
    for key in REQUIRED_CREATE_FIELDS[model_type]:
        fhir_json.pop(key)

    with pytest.raises(MissingRequiredFieldForCreate):
        validate_required_create_fields(fhir_json, model_type)


@pytest.mark.parametrize(
    "json_file", [{"contact": [{"telecom": [{"value": "foobar"}]}]}]
)
def test_email_validates(json_file):
    with pytest.raises(BadEmailFieldError):
        validate_contact_details(json_file)


@pytest.mark.parametrize(
    "expected_fields, expected_values",
    [
        (
            ["id", "name", "organisation", "owner"],
            ["f9518c12-6c83-4544-97db-d9dd1d64da97", "Test-Organization"],
        )
    ],
)
def test_create_product_team_from_fhir_organization(expected_fields, expected_values):
    fhir_json = read_test_data("organization-fhir-example.json")
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
    assert isinstance(fhir_model, StrictOrganization)
