from typing import TypeVar

from domain.core.product import ProductTeam
from domain.core.root import Root
from domain.fhir.r4 import cpm_model
from domain.fhir.r4.models import Organization
from domain.fhir.r4.strict_models import Organization as StrictOrganization
from pydantic import BaseModel

fhir_type = TypeVar("fhir_type")


def create_product_team_from_fhir_json(fhir_json: dict, **kwargs) -> ProductTeam:
    fhir_model = create_fhir_model_from_fhir_json(
        fhir_json=fhir_json, fhir_models=[StrictOrganization], our_model=Organization
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
        id=str(product_team.id),
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
    return org


def create_fhir_model_from_fhir_json(
    fhir_json: dict, fhir_models: list[BaseModel], our_model: BaseModel
) -> fhir_type:
    for fhir_model in fhir_models:
        fhir_model(**fhir_json)

    return our_model(**fhir_json)
