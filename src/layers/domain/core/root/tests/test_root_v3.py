from domain.core.ods_organisation.v3 import OdsOrganisation as OdsOrganisationV3
from domain.core.root.v3 import Root


def test_create_ods_organisation():
    org = Root.create_ods_organisation(ods_code="ABC")
    assert isinstance(org, OdsOrganisationV3)
