# all files listed here get downloaded to the paths listed in 'test_data_paths'
from collections import Counter, deque
from io import BytesIO

import boto3
import pytest
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property, parse_ldif
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.nhs_mhs_action import NhsMhsAction
from sds.domain.nhs_mhs_cp import NhsMhsCp
from sds.domain.nhs_mhs_service import NhsMhsService
from sds.domain.organizational_unit import OrganizationalUnit
from sds.domain.parse import parse_sds_record

from test_helpers.pytest_skips import memory_intensive
from test_helpers.terraform import read_terraform_output

BULK_SKIPS = [245315]
BULK_FILTER_SKIPS = [64320]


@pytest.mark.s3("sds/etl/bulk/1701246-mini.ldif")
def test_bulk_data_is_valid_sds_mini(test_data_paths):
    (ldif_path,) = test_data_paths

    unprocessed_records = deque(parse_ldif(file_opener=open, path_or_data=ldif_path))
    processed_records = []
    while unprocessed_records:
        distinguished_name, record = unprocessed_records[0]
        try:
            sds_record = parse_sds_record(
                distinguished_name=distinguished_name, record=record
            )
            processed_records.append(type(sds_record))
        except Exception as exception:
            processed_records.append(exception)
        else:
            unprocessed_records.popleft()

    assert Counter(processed_records) == {
        NhsMhsAction: 1660,
        NhsMhs: 1655,
        NhsMhsService: 297,
        NhsAccreditedSystem: 254,
        OrganizationalUnit: 1,
    }


@memory_intensive
@pytest.mark.s3("sds/etl/bulk/1701246.ldif")
def test_bulk_data_is_valid_sds_full(test_data_paths):
    (ldif_path,) = test_data_paths

    unprocessed_records = deque(parse_ldif(file_opener=open, path_or_data=ldif_path))

    index = 0
    processed_records = []
    while unprocessed_records:
        distinguished_name, record = unprocessed_records[0]
        try:
            if index not in BULK_SKIPS:
                sds_record = parse_sds_record(
                    distinguished_name=distinguished_name, record=record
                )
                processed_records.append(type(sds_record))
        except Exception as exception:
            processed_records.append(exception)
        else:
            unprocessed_records.popleft()
        index += 1

    assert Counter(processed_records) == {
        NhsMhs: 155574,
        NhsMhsAction: 155046,
        NhsMhsService: 26177,
        NhsAccreditedSystem: 5666,
        NhsMhsCp: 253,
        OrganizationalUnit: 1,
    }


@pytest.mark.integration
def test_filter_ldif_from_s3_by_property_mini():
    test_data_bucket = read_terraform_output("test_data_bucket.value")

    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_client=boto3.client("s3"),
        s3_path=f"s3://{test_data_bucket}/sds/etl/bulk/1701246-mini.ldif",
        filter_terms=[("objectClass", "nhsMHS"), ("objectClass", "nhsAS")],
    )

    unprocessed_records = deque(
        parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)
    )

    index = 0
    processed_records = []
    while unprocessed_records:
        distinguished_name, record = unprocessed_records[0]
        try:
            if index not in BULK_FILTER_SKIPS:
                sds_record = parse_sds_record(
                    distinguished_name=distinguished_name, record=record
                )
                processed_records.append(type(sds_record))
        except Exception as exception:
            processed_records.append(exception)
        else:
            unprocessed_records.popleft()
        index += 1

    assert Counter(processed_records) == {
        NhsMhs: 1655,
        NhsAccreditedSystem: 254,
    }


@memory_intensive
@pytest.mark.integration
def test_filter_ldif_from_s3_by_property_full():
    test_data_bucket = read_terraform_output("test_data_bucket.value")

    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_client=boto3.client("s3"),
        s3_path=f"s3://{test_data_bucket}/sds/etl/bulk/1701246.ldif",
        filter_terms=[("objectClass", "nhsMHS"), ("objectClass", "nhsAS")],
    )

    unprocessed_records = deque(
        parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)
    )

    index = 0
    processed_records = []
    while unprocessed_records:
        distinguished_name, record = unprocessed_records[0]
        try:
            if index not in BULK_FILTER_SKIPS:
                sds_record = parse_sds_record(
                    distinguished_name=distinguished_name, record=record
                )
                processed_records.append(type(sds_record))
        except Exception as exception:
            processed_records.append(exception)
        else:
            unprocessed_records.popleft()
        index += 1

    assert Counter(processed_records) == {
        NhsMhs: 155574,
        NhsAccreditedSystem: 5666,
    }
