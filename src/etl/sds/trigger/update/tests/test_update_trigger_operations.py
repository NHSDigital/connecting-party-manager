import os
from unittest import mock
from unittest.mock import Mock

import boto3
import pytest
from etl_utils.constants import CHANGELOG_NUMBER
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.trigger.update.operations import (
    BadChangeLogNumber,
    NoExistingChangeLogNumber,
    get_changelog_entries_from_ldap,
    get_current_changelog_number_from_s3,
    get_latest_changelog_number_from_ldap,
    parse_changelog_changes,
)

BUCKET_NAME = "my-bucket"


@pytest.fixture
def s3_client():
    with mock_aws(), mock.patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}):
        client = boto3.client("s3")
        client.create_bucket(Bucket=BUCKET_NAME)
        yield client


def test_get_current_changelog_number_from_s3_not_found(s3_client):
    with pytest.raises(NoExistingChangeLogNumber):
        get_current_changelog_number_from_s3(s3_client=s3_client, bucket=BUCKET_NAME)


@pytest.mark.parametrize("bad_changelog_number", ["[]", "", "foo", "123.4"])
def test_get_current_changelog_number_from_s3_bad_number(
    bad_changelog_number, s3_client: "S3Client"
):
    s3_client.put_object(
        Bucket=BUCKET_NAME, Key=CHANGELOG_NUMBER, Body=bad_changelog_number
    )
    with pytest.raises(BadChangeLogNumber):
        get_current_changelog_number_from_s3(s3_client=s3_client, bucket=BUCKET_NAME)


@pytest.mark.parametrize("good_changelog_number", [1, 1234])
def test_get_current_changelog_number_from_s3_good_number(
    good_changelog_number, s3_client: "S3Client"
):
    s3_client.put_object(
        Bucket=BUCKET_NAME, Key=CHANGELOG_NUMBER, Body=str(good_changelog_number)
    )
    assert (
        get_current_changelog_number_from_s3(s3_client=s3_client, bucket=BUCKET_NAME)
        == good_changelog_number
    )


def test_get_latest_changelog_number_from_ldap():
    assert (
        get_latest_changelog_number_from_ldap(ldap_connection=None, scope=None) == "123"
    )


def test_get_changelog_entries_from_ldap():
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_connection=Mock(),
        scope=None,
        current_changelog_number=12,
        latest_changelog_number=25,
    )
    assert len(ldif_collection) == 13


def test_get_changelog_entries_from_ldap_no_changes():
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_connection=Mock(),
        scope=None,
        current_changelog_number=12,
        latest_changelog_number=12,
    )
    assert len(ldif_collection) == 0


@pytest.mark.s3("sds/etl/changelog/75852519.ldif")
def test_parse_changelog_changes(test_data_paths):
    (path,) = test_data_paths
    with open(path) as f:
        ldif = f.read()

    assert (
        parse_changelog_changes(ldif=ldif)
        == """
objectClass: nhsas
objectClass: top
nhsApproverURP: System
nhsAsClient: K81045
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:operation:gpc.registerpatient-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:location-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:organization-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:patient-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:practitioner-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:organization-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:patient-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:practitioner-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:cancel:appointment-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:create:appointment-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:appointment-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:patient_appointments-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:slot-1
nhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:update:appointment-1
nhsDateApproved: 20240116173441
nhsDateRequested: 20240116173439
nhsIDCode: K81045
nhsMHSPartyKey: R3U6M-831547
nhsProductKey: 6255
nhsProductName: Continuum Health GPC
nhsProductVersion: Consumer AS
nhsRequestorURP: uniqueidentifier=865945089569,uniqueidentifier=065150856568,uid=798965609042,ou=people, o=nhs
uniqueIdentifier: 200000042019"""
    )
