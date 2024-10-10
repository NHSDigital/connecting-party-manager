from domain.core.product_team import ProductTeam
from domain.fhir.r4.cpm_model import OdsIdentifier, OdsReference
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir.r4.cpm_model import ProductTeamIdentifier


def create_fhir_model_from_product_team(
    product_team: ProductTeam,
) -> ProductTeamOrganization:
    return ProductTeamOrganization(
        resourceType=ProductTeamOrganization.__name__,
        identifier=[ProductTeamIdentifier(value=product_team.id)],
        name=product_team.name,
        partOf=OdsReference(identifier=OdsIdentifier(value=product_team.ods_code)),
    )
