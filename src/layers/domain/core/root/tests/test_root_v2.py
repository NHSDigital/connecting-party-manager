from domain.core.ods_organisation.v2 import OdsOrganisation as OdsOrganisationV2
from domain.core.root.v2 import Root


def test_create_ods_organisation():
    org = Root.create_ods_organisation(ods_code="ABC")
    assert isinstance(org, OdsOrganisationV2)
