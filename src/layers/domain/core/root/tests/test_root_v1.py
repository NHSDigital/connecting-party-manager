from domain.core.ods_organisation.v1 import OdsOrganisation as OdsOrganisationV1
from domain.core.root import Root


def test_create_ods_organisation():
    org = Root.create_ods_organisation(ods_code="ABC")
    assert isinstance(org, OdsOrganisationV1)
