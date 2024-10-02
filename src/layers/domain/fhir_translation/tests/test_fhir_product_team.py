from domain.core.product_team import ProductTeam
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir_translation.product_team import create_fhir_model_from_product_team

from test_helpers.sample_data import ORGANISATION


def test_product_team_translation():
    """
    Tests that 'create_product_team_from_fhir_org_json'
    is the compliment of 'create_fhir_model_from_product_team'
    """
    product_team = ProductTeam(
        id="f9518c12-6c83-4544-97db-d9dd1d64da97",
        name="Test-Organization",
        ods_code="F5H1R",
    )
    fhir_json = ORGANISATION
    assert isinstance(product_team, ProductTeam)

    fhir_org = create_fhir_model_from_product_team(product_team=product_team)
    assert isinstance(fhir_org, ProductTeamOrganization)

    assert fhir_org.dict() == fhir_json
