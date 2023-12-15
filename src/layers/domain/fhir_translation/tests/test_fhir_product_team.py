from domain.core.product_team import ProductTeam
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir_translation.product_team import (
    create_fhir_model_from_product_team,
    create_product_team_from_fhir_org_json,
)
from domain.fhir_translation.tests.utils import read_test_data


def test_product_team_translation():
    """
    Tests that 'create_product_team_from_fhir_org_json'
    is the compliment of 'create_fhir_model_from_product_team'
    """

    fhir_json = read_test_data("organization-fhir-example-required.json")
    product_team = create_product_team_from_fhir_org_json(fhir_org_json=fhir_json)
    assert isinstance(product_team, ProductTeam)

    fhir_org = create_fhir_model_from_product_team(product_team=product_team)
    assert isinstance(fhir_org, ProductTeamOrganization)

    assert fhir_org.dict() == fhir_json
