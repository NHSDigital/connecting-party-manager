from domain.core.ods_organisation import OdsOrganisation
from domain.core.root import Root


def test_create_ods_organisation():
    org = Root.create_ods_organisation(ods_code="ABC")
    assert isinstance(org, OdsOrganisation)
