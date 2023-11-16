import re
from typing import TypeVar, Union

from domain.core.error import (
    BadEmailFieldError,
    FhirValidationError,
    MissingRequiredFieldForCreate,
)
from domain.core.product import ProductTeam
from domain.core.root import Root
from domain.fhir.r4 import cpm_model
from domain.fhir.r4.models import Organization
from domain.fhir.r4.strict_models import Organization as StrictOrganization
from pydantic import BaseModel

from .constants import EMPTY_VALUES, JSON_TYPES, REQUIRED_CREATE_FIELDS

fhir_type = TypeVar("fhir_type")


def strip_empty_json_paths(
    json: Union[list[dict], dict], raise_on_discovery=False
) -> Union[list[dict], dict]:
    stripped_json = json
    modified = False
    if type(json) is list:
        stripped_json = []
        for item in json:
            if type(item) in JSON_TYPES:
                item = strip_empty_json_paths(item)
            if item in EMPTY_VALUES:
                modified = True
            else:
                stripped_json.append(item)
    elif type(json) is dict:
        stripped_json = {}
        for key, value in json.items():
            if type(value) in JSON_TYPES:
                value = strip_empty_json_paths(value)
            if value in EMPTY_VALUES:
                modified = True
            else:
                stripped_json[key] = value

    if raise_on_discovery:
        if stripped_json != json:
            raise FhirValidationError(f"Invalid FHIR, Empty values exist")

    return strip_empty_json_paths(stripped_json) if modified else stripped_json


def validate_no_extra_fields(input_fhir_json, output_fhir_json):
    if input_fhir_json != output_fhir_json:
        raise FhirValidationError("Input FHIR JSON has additional non-FHIR fields.")


def validate_required_create_fields(request_body_json, model_type):
    for field in REQUIRED_CREATE_FIELDS[model_type]:
        if field not in request_body_json:
            raise MissingRequiredFieldForCreate(field)


def validate_contact_details(input_fhir_json):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    email = (
        input_fhir_json.get("contact", [{}])[0]
        .get("telecom", [{}])[0]
        .get("value", None)
    )
    if not re.match(email_pattern, email):
        raise BadEmailFieldError()


def create_product_team_from_fhir_json(fhir_json: dict, **kwargs) -> ProductTeam:
    stripped_fhir_json = strip_empty_json_paths(json=fhir_json)
    fhir_model = create_fhir_model_from_fhir_json(
        fhir_json=stripped_fhir_json,
        model=Organization,
        strict_model=StrictOrganization,
        model_type="Organization",
    )
    org = Root.create_ods_organisation(
        id=fhir_model.partOf.identifier.id,
        name=fhir_model.partOf.identifier.value,
    )
    user = Root.create_user(
        id=fhir_model.contact[0].telecom[0].value, name=fhir_model.contact[0].name.text
    )
    (result, event) = org.create_product_team(fhir_model.id, fhir_model.name, user)
    return result


def create_fhir_model_from_product_team(product_team: ProductTeam, **kwargs) -> dict:
    org = cpm_model.Organization(
        resourceType="Organization",
        id=product_team.id,
        name=product_team.name,
        partOf=cpm_model.Reference(
            identifier=cpm_model.Identifier(
                id=product_team.organisation.id,
                value=product_team.organisation.name,
            )
        ),
        contact=[
            cpm_model.OrganizationContact(
                name=cpm_model.HumanName(text=product_team.owner.name),
                telecom=[
                    cpm_model.ContactPoint(system="email", value=product_team.owner.id)
                ],
            )
        ],
    )
    return org.dict()

    # product_team_dict = product_team.__dict__
    # product_team_dict["resourceType"] = "Organization"
    # product_team_dict["id"] = str(product_team_dict["id"])
    # product_team_dict["organisation"] = product_team_dict["organisation"].__dict__
    # product_team_dict["owner"] = product_team_dict["owner"].__dict__
    # org = StrictOrganization(
    #     id=product_team_dict["id"],
    #     resourceType=product_team_dict["resourceType"],
    #     name=product_team_dict["name"],
    #     partOf={
    #         "id": product_team_dict["organisation"]["id"],
    #         "identifier": {
    #             "id": product_team_dict["organisation"]["id"],
    #             "value": product_team_dict["organisation"]["name"],
    #         },
    #     },
    #     contact=[
    #         {
    #             "name": {"text": product_team_dict["owner"]["name"]},
    #             "telecom": [
    #                 {"system": "email", "value": product_team_dict["owner"]["id"]}
    #             ],
    #         }
    #     ],
    # )

    # return org


def create_fhir_model_from_fhir_json(
    fhir_json: dict, fhir_models: list[BaseModel], our_model: BaseModel
) -> fhir_type:
    for fhir_model in fhir_models:
        fhir_model(**fhir_json)

    # fhir_strict_model = strict_model(**fhir_json)
    # cpm_model.Organization(**fhir_json)

    # validate_required_create_fields(fhir_json, model_type)
    # validate_no_extra_fields(
    #     input_fhir_json=fhir_json,
    #     output_fhir_json=fhir_strict_model.dict(exclude_none=True),
    # )
    # validate_contact_details(input_fhir_json=fhir_json)
    # strip_empty_json_paths(json=fhir_json)

    return our_model(**fhir_json)
