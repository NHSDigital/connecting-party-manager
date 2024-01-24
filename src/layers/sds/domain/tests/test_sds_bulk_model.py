# all files listed here get downloaded to the paths listed in 'test_data_paths'
from collections import Counter
from io import BytesIO

import pytest
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.nhs_mhs_action import NhsMhsAction
from sds.domain.nhs_mhs_cp import NhsMhsCp
from sds.domain.nhs_mhs_service import NhsMhsService
from sds.domain.organizational_unit import OrganizationalUnit
from sds.domain.parse import parse_ldif_to_sds

from test_helpers.terraform import read_terraform_output


@pytest.mark.s3("sds/etl/bulk/1701246-mini.ldif")
def test_bulk_data_is_valid_sds_mini(test_data_paths):
    (ldif_path,) = test_data_paths

    processed_records = [
        type(sds_record) if not isinstance(sds_record, ExceptionGroup) else sds_record
        for sds_record in parse_ldif_to_sds(file_opener=open, path_or_data=ldif_path)
    ]

    assert Counter(processed_records) == {
        NhsMhsAction: 1660,
        NhsMhs: 1655,
        NhsMhsService: 297,
        NhsAccreditedSystem: 254,
        OrganizationalUnit: 1,
    }


@pytest.mark.s3("sds/etl/bulk/1701246.ldif")
def test_bulk_data_is_valid_sds_full(test_data_paths):
    (ldif_path,) = test_data_paths

    processed_records = [
        type(sds_record)
        for sds_record in parse_ldif_to_sds(
            file_opener=open, path_or_data=ldif_path, skip=[245315]
        )
    ]

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
        bucket=test_data_bucket,
        key="sds/etl/bulk/1701246-mini.ldif",
        filter_terms=[("objectClass", "nhsMHS"), ("objectClass", "nhsAS")],
    )

    processed_records = [
        type(sds_record)
        for sds_record in parse_ldif_to_sds(
            file_opener=BytesIO, path_or_data=filtered_ldif
        )
    ]

    assert Counter(processed_records) == {
        NhsMhs: 1655,
        NhsAccreditedSystem: 254,
    }


@pytest.mark.integration
def test_filter_ldif_from_s3_by_property_full():
    test_data_bucket = read_terraform_output("test_data_bucket.value")

    filtered_ldif = filter_ldif_from_s3_by_property(
        bucket=test_data_bucket,
        key="sds/etl/bulk/1701246.ldif",
        filter_terms=[("objectClass", "nhsMHS"), ("objectClass", "nhsAS")],
    )

    processed_records = [
        type(sds_record)
        for sds_record in parse_ldif_to_sds(
            file_opener=BytesIO, path_or_data=filtered_ldif, skip=[64320]
        )
    ]

    assert Counter(processed_records) == {
        NhsMhs: 155574,
        NhsAccreditedSystem: 5666,
    }
