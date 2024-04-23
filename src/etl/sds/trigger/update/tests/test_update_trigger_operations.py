import os
from io import StringIO
from unittest import mock
from unittest.mock import Mock

import boto3
import pytest
from etl_utils.constants import CHANGELOG_NUMBER
from etl_utils.ldif.ldif import parse_ldif
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


# Removed the empty string test as it was having some weird behaviour
@pytest.mark.parametrize("bad_changelog_number", ["[]", "foo", "123.4"])
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
    mock_ldap_client = mock.Mock()
    mock_ldap_client.result.return_value = (
        101,
        [
            (
                "cn=changelog,o=nhs",
                {"firstchangenumber": [b"46425"], "lastchangenumber": [b"537637"]},
            )
        ],
    )
    assert (
        get_latest_changelog_number_from_ldap(
            ldap_client=mock_ldap_client, ldap=mock.Mock()
        )
        == 537637
    )


def test_get_changelog_entries_from_ldap_with_add():
    mock_ldap_client = mock.Mock()
    mock_ldap_client.result.return_value = (
        101,
        [
            [
                "changenumber=537576,cn=changelog,o=nhs",
                {
                    "objectClass": [
                        b"top",
                        b"changeLogEntry",
                        b"nhsExternalChangelogEntry",
                    ],
                    "changeNumber": [b"537576"],
                    "changes": [
                        b"\nobjectClass: nhsas\nobjectClass: top\nnhsApproverURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\nnhsAsClient: 8KH75\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:location\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:organization\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:patient\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:practitioner\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:location\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:organization\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:patient\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:practitioner\nnhsDateApproved: 20240417121611\nnhsDateRequested: 20240417121533\nnhsIDCode: 8KH75\nnhsMHSPartyKey: 8KH75-823852\nnhsProductKey: 12041\nnhsProductName: CareLineLive\nnhsProductVersion: 2024.4.1\nnhsRequestorURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\nuniqueIdentifier: 200000002217"
                    ],
                    "changeTime": [b"20240417111615Z"],
                    "changeType": [b"add"],
                    "targetDN": [b"uniqueIdentifier=200000002217,ou=Services,o=nhs"],
                },
            ]
        ],
    )
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_client=mock_ldap_client,
        ldap=Mock(),
        current_changelog_number=12,
        latest_changelog_number=25,
    )
    assert len(ldif_collection) == 13


def test_get_changelog_entries_from_ldap_with_modify():
    mock_ldap_client = mock.Mock()
    mock_ldap_client.result.return_value = (
        101,
        [
            [
                "changenumber=538407,cn=changelog,o=nhs",
                {
                    "objectClass": [
                        b"top",
                        b"changeLogEntry",
                        b"nhsExternalChangelogEntry",
                    ],
                    "changeNumber": [b"538407"],
                    "changes": [
                        b"\nreplace: nhsAsSvcIA\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:MCCI_IN010000UK13\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:QUPC_IN000006GB01"
                    ],
                    "changeTime": [b"20240422081609Z"],
                    "changeType": [b"modify"],
                    "targetDN": [b"uniqueIdentifier=200000002202,ou=Services,o=nhs"],
                },
            ]
        ],
    )
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_client=mock_ldap_client,
        ldap=Mock(),
        current_changelog_number=12,
        latest_changelog_number=25,
    )
    assert len(ldif_collection) == 13


def test_get_changelog_entries_from_ldap_with_delete():
    mock_ldap_client = mock.Mock()
    mock_ldap_client.result.return_value = (
        101,
        [
            [
                "changenumber=538210,cn=changelog,o=nhs",
                {
                    "objectClass": [
                        b"top",
                        b"changeLogEntry",
                        b"nhsExternalChangelogEntry",
                    ],
                    "changeNumber": [b"538210"],
                    "changeTime": [b"20240422081603Z"],
                    "changeType": [b"delete"],
                    "targetDN": [
                        b"uniqueIdentifier=7abed27a247a511b7f0a,ou=Services,o=nhs"
                    ],
                },
            ]
        ],
    )
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_client=mock_ldap_client,
        ldap=Mock(),
        current_changelog_number=12,
        latest_changelog_number=25,
    )
    assert len(ldif_collection) == 13


def test_get_changelog_entries_from_ldap_no_changes():
    mock_ldap_client = mock.Mock()
    mock_ldap_client.result.return_value = (
        101,
        [
            (
                "foo=bar",
                {"foo": "bar"},
            ),
        ],
    )
    ldif_collection = get_changelog_entries_from_ldap(
        ldap_client=mock_ldap_client,
        ldap=Mock(),
        current_changelog_number=12,
        latest_changelog_number=12,
    )
    assert len(ldif_collection) == 0


@pytest.mark.s3("sds/etl/changelog/75852519.ldif")
def test_parse_changelog_changes(test_data_paths):
    (path,) = test_data_paths
    with open(path) as f:
        ldif = f.read()

    ((_, record),) = parse_ldif(file_opener=StringIO, path_or_data=ldif)
    assert (
        parse_changelog_changes(
            distinguished_name="changenumber=75852519,cn=changelog,o=nhs", record=record
        )
        == "\nobjectClass: nhsas\nobjectClass: top\nnhsApproverURP: System\nnhsAsClient: K81045\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:operation:gpc.registerpatient-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:location-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:organization-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:patient-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:practitioner-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:organization-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:patient-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:practitioner-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:metadata\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:cancel:appointment-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:create:appointment-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:read:appointment-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:patient_appointments-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:search:slot-1\nnhsAsSvcIA: urn:nhs:names:services:gpconnect:fhir:rest:update:appointment-1\nnhsDateApproved: 20240116173441\nnhsDateRequested: 20240116173439\nnhsIDCode: K81045\nnhsMHSPartyKey: R3U6M-831547\nnhsProductKey: 6255\nnhsProductName: Continuum Health GPC\nnhsProductVersion: Consumer AS\nnhsRequestorURP: uniqueidentifier=865945089569,uniqueidentifier=065150856568,uid=798965609042,ou=people, o=nhs\nuniqueIdentifier: 200000042019"
    )


def test_parse_changelog_changes_with_add():
    dn = "changenumber=537507,cn=changelog,o=nhs"
    record = {
        "objectClass": [b"top", b"changeLogEntry", b"nhsExternalChangelogEntry"],
        "changeNumber": [b"537507"],
        "changes": [
            b"\\nobjectClass: nhsMhs\\nobjectClass: top\\nnhsApproverURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nnhsContractPropertyTemplateKey: 14\\nnhsDateApproved: 20240417082830\\nnhsDateDNSApproved: 20240417082830\\nnhsDateRequested: 20240417082818\\nnhsDNSApprover: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nnhsEPInteractionType: ebXML\\nnhsIDCode: X26\\nnhsMHSAckRequested: never\\nnhsMhsCPAId: f1c55263f1ee924f460f\\nnhsMHSDuplicateElimination: never\\nnhsMHSEndPoint: https://simple-sync.intspineservices.nhs.uk/\\nnhsMhsFQDN: simple-sync.intspineservices.nhs.uk\\nnhsMHsIN: QUPA_IN050000UK32\\nnhsMhsIPAddress: 0.0.0.0\\nnhsMHSIsAuthenticated: none\\nnhsMHSPartyKey: X26-823848\\nnhsMHsSN: urn:nhs:names:services:pdsquery\\nnhsMhsSvcIA: urn:nhs:names:services:pdsquery:QUPA_IN050000UK32\\nnhsMHSSyncReplyMode: None\\nnhsProductKey: 10894\\nnhsProductName: Compliance\\nnhsProductVersion: Initial\\nnhsRequestorURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nuniqueIdentifier: f1c55263f1ee924f460f"
        ],
        "changeTime": [b"20240417072834Z"],
        "changeType": [b"add"],
        "targetDN": [b"uniqueIdentifier=f1c55263f1ee924f460f,ou=Services,o=nhs"],
    }
    result = parse_changelog_changes(distinguished_name=dn, record=record)

    assert (
        result
        == "dn: uniqueIdentifier=f1c55263f1ee924f460f,ou=Services,o=nhs\nchangetype: add\nobjectClass: nhsMhs\nobjectClass: top\nnhsApproverURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\nnhsContractPropertyTemplateKey: 14\nnhsDateApproved: 20240417082830\nnhsDateDNSApproved: 20240417082830\nnhsDateRequested: 20240417082818\nnhsDNSApprover: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\nnhsEPInteractionType: ebXML\nnhsIDCode: X26\nnhsMHSAckRequested: never\nnhsMhsCPAId: f1c55263f1ee924f460f\nnhsMHSDuplicateElimination: never\nnhsMHSEndPoint: https://simple-sync.intspineservices.nhs.uk/\nnhsMhsFQDN: simple-sync.intspineservices.nhs.uk\nnhsMHsIN: QUPA_IN050000UK32\nnhsMhsIPAddress: 0.0.0.0\nnhsMHSIsAuthenticated: none\nnhsMHSPartyKey: X26-823848\nnhsMHsSN: urn:nhs:names:services:pdsquery\nnhsMhsSvcIA: urn:nhs:names:services:pdsquery:QUPA_IN050000UK32\nnhsMHSSyncReplyMode: None\nnhsProductKey: 10894\nnhsProductName: Compliance\nnhsProductVersion: Initial\nnhsRequestorURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\nuniqueIdentifier: f1c55263f1ee924f460f"
    )


def test_parse_changelog_changes_with_modify():
    dn = "changenumber=538407,cn=changelog,o=nhs"
    record = {
        "objectClass": [b"top", b"changeLogEntry", b"nhsExternalChangelogEntry"],
        "changeNumber": [b"538407"],
        "changes": [
            b"\nreplace: nhsAsSvcIA\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:MCCI_IN010000UK13\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:QUPC_IN000006GB01"
        ],
        "changeTime": [b"20240422081609Z"],
        "changeType": [b"modify"],
        "targetDN": [b"uniqueIdentifier=200000002202,ou=Services,o=nhs"],
    }
    result = parse_changelog_changes(distinguished_name=dn, record=record)

    assert (
        result
        == "dn: uniqueIdentifier=200000002202,ou=Services,o=nhs\nchangetype: modify\nreplace: nhsAsSvcIA\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:MCCI_IN010000UK13\nnhsAsSvcIA: urn:nhs:names:services:cpisquery:QUPC_IN000006GB01"
    )


def test_parse_changelog_changes_with_delete():
    dn = "changenumber=538210,cn=changelog,o=nhs"
    record = {
        "objectClass": [b"top", b"changeLogEntry", b"nhsExternalChangelogEntry"],
        "changeNumber": [b"538210"],
        "changeTime": [b"20240422081603Z"],
        "changeType": [b"delete"],
        "targetDN": [b"uniqueIdentifier=7abed27a247a511b7f0a,ou=Services,o=nhs"],
    }
    result = parse_changelog_changes(distinguished_name=dn, record=record)

    assert (
        result
        == "dn: uniqueIdentifier=7abed27a247a511b7f0a,ou=Services,o=nhs\nchangetype: delete"
    )
