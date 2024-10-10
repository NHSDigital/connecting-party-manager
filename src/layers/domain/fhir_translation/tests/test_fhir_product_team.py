from domain.core.product_team.v3 import ProductTeam
from domain.fhir.r4.cpm_model import Organization as ProductTeamOrganization
from domain.fhir_translation.product_team import create_fhir_model_from_product_team

from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID


def test_product_team_translation():
    """
    Tests that 'non FHIR ProductTeam'
    is the compliment of 'create_fhir_model_from_product_team'
    """
    product_team = ProductTeam(
        name=CPM_PRODUCT_TEAM_NO_ID["name"],
        ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"],
        keys=CPM_PRODUCT_TEAM_NO_ID["keys"],
    )
    assert isinstance(product_team, ProductTeam)

    fhir_org = create_fhir_model_from_product_team(product_team=product_team)
    assert isinstance(fhir_org, ProductTeamOrganization)

    org = fhir_org.dict()
    assert CPM_PRODUCT_TEAM_NO_ID["ods_code"] in org["identifier"][0]["value"]
    assert org["partOf"]["identifier"]["value"] == CPM_PRODUCT_TEAM_NO_ID["ods_code"]
    assert org["name"] == CPM_PRODUCT_TEAM_NO_ID["name"]
