from api.createProductTeam.tests.data import organisation

from ..steps import _parse_fhir_organisation


def test__create_product_team():
    org = _parse_fhir_organisation(organisation=organisation)
    assert org.dict(exclude_none=True) == organisation
