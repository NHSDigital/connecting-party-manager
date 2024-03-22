from io import StringIO

import pytest
from etl_utils.ldif.ldif import parse_ldif
from etl_utils.ldif.model import DistinguishedName
from sds.domain.changelog import ChangelogRecord
from sds.domain.parse import parse_sds_record


# all files listed here get downloaded to the paths listed in 'test_data_paths'
@pytest.mark.s3("sds/etl/changelog/75852519.ldif")
def test_changelog_model_against_changelog_data(test_data_paths):
    (ldif_path,) = test_data_paths

    ldif_lines = parse_ldif(file_opener=open, path_or_data=ldif_path)

    # Implicit check that one changelog line is expected
    ((distinguished_name, record),) = ldif_lines

    # Implicit check that it parses
    changelog_record = ChangelogRecord(
        _distinguished_name=distinguished_name,
        **record,
    )

    # Check that the record has been parsed correctly
    assert changelog_record.distinguished_name.change_number == "75852519"
    assert changelog_record.distinguished_name.common_name == "changelog"
    assert changelog_record.distinguished_name.organisation == "nhs"

    assert changelog_record.object_class == "changeLogEntry"
    assert (
        changelog_record.change_number
        == changelog_record.distinguished_name.change_number
    )
    assert changelog_record.change_time == "20240116173441Z"
    assert changelog_record.change_type == "add"
    assert changelog_record.target_distinguished_name == DistinguishedName(
        parts=(("o", "nhs"), ("ou", "Services"), ("uniqueIdentifier", "200000042019"))
    )


# all files listed here get downloaded to the paths listed in 'test_data_paths'
@pytest.mark.s3("sds/etl/changelog/75852519.ldif")
def test_changelog_changes_are_valid_ldif(test_data_paths):
    (ldif_path,) = test_data_paths

    ldif_lines = parse_ldif(file_opener=open, path_or_data=ldif_path)

    # Implicit check that one changelog line is expected
    ((distinguished_name, record),) = ldif_lines

    # Implicit check that it parses
    changelog_record = ChangelogRecord(
        _distinguished_name=distinguished_name,
        **record,
    )

    # HACK THE RECORD - FOR SOME REASON DOESN'T START WITH DN LINE?
    changelog_record.changes = (
        "dn: uniqueidentifier=200000042019,ou=services,o=nhs" + changelog_record.changes
    )

    # Check that the change itself is valid LDIF
    nested_ldif_lines = list(
        parse_ldif(file_opener=StringIO, path_or_data=changelog_record.changes)
    )
    assert len(nested_ldif_lines) == 1

    # Check that the change is a valid SDS record
    ((nested_distinguished_name, nested_record),) = nested_ldif_lines
    sds_record = parse_sds_record(
        distinguished_name=nested_distinguished_name, record=nested_record
    )
    assert sds_record.dict() == {
        "change_type": "add",
        "description": None,
        "nhs_approver_urp": "System",
        "nhs_as_acf": None,
        "nhs_as_category_bag": None,
        "nhs_as_client": {"K81045"},
        "nhs_as_svc_ia": {
            "urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord",
            "urn:nhs:names:services:gpconnect:fhir:operation:gpc.registerpatient-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:cancel:appointment-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:create:appointment-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:appointment-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:location-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:metadata",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:metadata-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:organization-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:patient-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:read:practitioner-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:search:organization-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:search:patient-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:search:patient_appointments-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:search:practitioner-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:search:slot-1",
            "urn:nhs:names:services:gpconnect:fhir:rest:update:appointment-1",
        },
        "nhs_date_approved": "20240116173441",
        "nhs_date_requested": "20240116173439",
        "nhs_id_code": "K81045",
        "nhs_mhs_manufacturer_org": None,
        "nhs_mhs_party_key": "R3U6M-831547",
        "nhs_product_key": "6255",
        "nhs_product_name": "Continuum Health GPC",
        "nhs_product_version": "Consumer AS",
        "nhs_requestor_urp": "uniqueidentifier=865945089569,uniqueidentifier=065150856568,uid=798965609042,ou=people, o=nhs",
        "nhs_temp_uid": None,
        "object_class": "nhsas",
        "unique_identifier": "200000042019",
    }
