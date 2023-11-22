from typing import TypeVar

from domain.core.product_team import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root
from domain.fhir.r4 import Organization, StrictOrganization, cpm_model
from event.response.validation_errors import mark_validation_errors_as_inbound
from pydantic import BaseModel

fhir_type = TypeVar("fhir_type")


def create_product_team_from_fhir_org_json(
    fhir_org_json: dict, **kwargs
) -> tuple[ProductTeam, ProductTeamCreatedEvent]:
    fhir_org = create_fhir_model_from_fhir_json(
        fhir_json=fhir_org_json,
        fhir_models=[Organization, StrictOrganization],
        our_model=cpm_model.Organization,
    )
    org = Root.create_ods_organisation(
        ods_code=fhir_org.partOf.identifier.id,
        name=fhir_org.partOf.identifier.value,
    )
    product_team, event = org.create_product_team(id=fhir_org.id, name=fhir_org.name)
    return product_team, event


def create_fhir_model_from_product_team(product_team: ProductTeam, **kwargs) -> dict:
    org = cpm_model.Organization(
        resourceType="Organization",
        id=str(product_team.id),
        name=product_team.name,
        partOf=cpm_model.Reference(
            identifier=cpm_model.Identifier(
                id=product_team.ods_code,
                value=product_team.ods_code,
            )
        ),
    )
    return org


@mark_validation_errors_as_inbound
def create_fhir_model_from_fhir_json(
    fhir_json: dict, fhir_models: list[BaseModel], our_model: fhir_type
) -> fhir_type:
    # Validate and parse against out ruleset
    fhir_model = our_model(**fhir_json)
    # Validate against the FHIR ruleset
    for _fhir_model in fhir_models:
        _fhir_model(**fhir_json)
    return fhir_model
