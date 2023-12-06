from domain.core.product_team import ProductTeam
from domain.core.root import Root
from domain.fhir.r4 import Organization, StrictOrganization
from domain.fhir.r4.cpm_model import Identifier, OdsIdentifier
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir.r4.cpm_model import Reference
from event.response.validation_errors import mark_validation_errors_as_inbound

from .parse import create_fhir_model_from_fhir_json


@mark_validation_errors_as_inbound
def create_product_team_from_fhir_org_json(
    fhir_org_json: dict, **kwargs
) -> ProductTeam:
    fhir_org = create_fhir_model_from_fhir_json(
        fhir_json=fhir_org_json,
        fhir_models=[Organization, StrictOrganization],
        our_model=ProductTeamOrganization,
    )
    org = Root.create_ods_organisation(ods_code=fhir_org.partOf.identifier.value)
    (identifier,) = fhir_org.identifier
    product_team = org.create_product_team(id=identifier.value, name=fhir_org.name)  # type: ignore
    return product_team


def create_fhir_model_from_product_team(
    product_team: ProductTeam, **kwargs
) -> ProductTeamOrganization:
    return ProductTeamOrganization(
        resourceType=ProductTeamOrganization.__name__,
        identifier=[Identifier(value=product_team.id)],
        name=product_team.name,
        partOf=Reference(identifier=OdsIdentifier(value=product_team.ods_code)),
    )
