from typing import TypeVar

from domain.core.product import ProductTeam
from domain.core.root import Root
from domain.fhir.r4 import Organization, StrictOrganization, cpm_model
from pydantic import BaseModel

fhir_type = TypeVar("fhir_type")


def create_product_team_from_fhir_org_json(
    fhir_org_json: dict, **kwargs
) -> ProductTeam:
    fhir_org = create_fhir_model_from_fhir_json(
        fhir_json=fhir_org_json,
        fhir_models=[Organization, StrictOrganization],
        our_model=cpm_model.Organization,
    )
    org = Root.create_ods_organisation(
        id=fhir_org.partOf.identifier.id,
        name=fhir_org.partOf.identifier.value,
    )
    user = Root.create_user(
        id=fhir_org.contact[0].telecom[0].value, name=fhir_org.contact[0].name.text
    )
    (product_team, event) = org.create_product_team(fhir_org.id, fhir_org.name, user)
    return product_team


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
    fhir_json: dict, fhir_models: list[BaseModel], our_model: fhir_type
) -> fhir_type:
    # Validate against the FHIR ruleset
    for fhir_model in fhir_models:
        fhir_model(**fhir_json)
    # Validate and parse against out ruleset
    return our_model(**fhir_json)