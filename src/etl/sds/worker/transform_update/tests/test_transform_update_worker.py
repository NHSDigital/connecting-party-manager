import os
import re
from collections import deque
from itertools import permutations
from typing import Callable
from unittest import mock
from uuid import uuid4

import pytest
from domain.core.device.v2 import DeviceType
from domain.core.root.v2 import Root
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.worker.transform_update.utils import export_events

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"

GOOD_SDS_RECORD_AS_JSON = {
    "description": None,
    "distinguished_name": {
        "organisation": "nhs",
        "organisational_unit": "services",
        "unique_identifier": None,
    },
    "nhs_approver_urp": "uniqueIdentifier=562983788547,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs",
    "nhs_as_acf": None,
    "nhs_as_category_bag": None,
    "nhs_as_client": ["RVL"],
    "nhs_as_svc_ia": ["urn:nhs:names:services:pds:QUPA_IN040000UK01"],
    "nhs_date_approved": "20090601140104",
    "nhs_date_requested": "20090601135904",
    "nhs_id_code": "RVL",
    "nhs_mhs_manufacturer_org": "LSP04",
    "nhs_mhs_party_key": "RVL-806539",
    "nhs_product_key": "634",
    "nhs_product_name": "Cerner Millennium",
    "nhs_product_version": "2005.02",
    "nhs_requestor_urp": "uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs",
    "nhs_temp_uid": "9713",
    "object_class": "nhsAS",
    "unique_identifier": "000428682512",
}

BAD_SDS_RECORD_AS_JSON = {}

FATAL_SDS_RECORD_AS_JSON = "<not_json"


PROCESSED_SDS_JSON_RECORD = {}  # dummy value, doesn't matter for transform


@pytest.fixture
def mock_s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ,
        {
            "ETL_BUCKET": BUCKET_NAME,
            "TABLE_NAME": TABLE_NAME,
            "AWS_DEFAULT_REGION": "us-east-1",
        },
        clear=True,
    ):
        from etl.sds.worker.transform_update import transform_update

        transform_update.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield transform_update.S3_CLIENT


@pytest.fixture
def put_object(mock_s3_client: S3Client):
    return lambda key, body: (
        mock_s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=body)
    )


@pytest.fixture
def get_object(mock_s3_client: S3Client) -> bytes:
    return lambda key: (
        mock_s3_client.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read()
    )


def test_transform_worker_pass_no_dupes(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):
    from etl.sds.worker.transform_update import transform_update

    initial_unprocessed_data = deque([GOOD_SDS_RECORD_AS_JSON])
    initial_processed_data = deque([])

    # Initial state
    n_initial_unprocessed = len(initial_unprocessed_data)
    n_initial_processed = len(initial_processed_data)
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(initial_unprocessed_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    # Execute the transform worker
    response = transform_update.handler(event={}, context=None)

    assert response == {
        "stage_name": "transform",
        "processed_records": n_initial_processed + 4 * n_initial_unprocessed,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=WorkerKey.LOAD)
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(pkl_loads_lz4(final_processed_data))

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert n_final_processed == n_initial_processed + 4 * n_initial_unprocessed
    assert n_final_unprocessed == 0


@pytest.mark.parametrize("max_records", range(1, 10))
def test_transform_worker_pass_no_dupes_max_records(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
    max_records: int,
):
    from etl.sds.worker.transform_update import transform_update

    initial_unprocessed_data = deque([GOOD_SDS_RECORD_AS_JSON] * 10)
    initial_processed_data = deque([])

    # Initial state
    n_initial_unprocessed = len(initial_unprocessed_data)
    n_initial_processed = len(initial_processed_data)
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(initial_unprocessed_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    n_total_processed_records_expected = 0
    n_unprocessed_records = n_initial_unprocessed
    while n_unprocessed_records > 0:
        n_newly_processed_records_expected = min(n_unprocessed_records, max_records)
        n_unprocessed_records_expected = (
            n_unprocessed_records - n_newly_processed_records_expected
        )
        n_total_processed_records_expected += 4 * n_newly_processed_records_expected

        # Execute the transform worker
        response = transform_update.handler(
            event={"max_records": max_records}, context=None
        )
        assert response == {
            "stage_name": "transform",
            "processed_records": n_total_processed_records_expected,
            "unprocessed_records": n_unprocessed_records_expected,
            "error_message": None,
        }

        n_unprocessed_records = response["unprocessed_records"]

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=WorkerKey.LOAD)
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(pkl_loads_lz4(final_processed_data))

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert n_final_processed == n_initial_processed + 4 * n_initial_unprocessed
    assert n_final_unprocessed == 0


@pytest.mark.parametrize(
    "initial_unprocessed_data",
    permutations(
        [BAD_SDS_RECORD_AS_JSON, GOOD_SDS_RECORD_AS_JSON, GOOD_SDS_RECORD_AS_JSON]
    ),
)
def test_transform_worker_bad_record(
    initial_unprocessed_data: str,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):
    from etl.sds.worker.transform_update import transform_update

    _initial_unprocessed_data = pkl_dumps_lz4(deque(initial_unprocessed_data))
    bad_record_index = initial_unprocessed_data.index(BAD_SDS_RECORD_AS_JSON)

    # Initial state
    n_initial_processed = 5
    n_initial_unprocessed = len(initial_unprocessed_data)
    initial_processed_data = pkl_dumps_lz4(
        deque(n_initial_processed * [PROCESSED_SDS_JSON_RECORD])
    )
    put_object(key=WorkerKey.TRANSFORM, body=_initial_unprocessed_data)
    put_object(key=WorkerKey.LOAD, body=initial_processed_data)

    # Execute the transform worker
    response = transform_update.handler(event={}, context=None)

    response["error_message"] = response["error_message"].split("\n")[:6]

    assert response == {
        "stage_name": "transform",
        "processed_records": n_initial_processed + 4 * bad_record_index,
        "unprocessed_records": n_initial_unprocessed - bad_record_index,
        "error_message": [
            "The following errors were encountered",
            "  -- Error 1 (KeyError) --",
            f"  Failed to parse record {bad_record_index}",
            "  {}",
            "  'object_class'",
            "Traceback (most recent call last):",
        ],
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=WorkerKey.LOAD)
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(pkl_loads_lz4(final_processed_data))

    # Confirm that there are still unprocessed records, and that there may have been
    # some records processed successfully
    assert n_final_unprocessed > 0
    assert n_final_processed == n_initial_processed + 4 * bad_record_index
    assert n_final_unprocessed == n_initial_unprocessed - bad_record_index


def test_transform_worker_fatal_record(
    put_object: Callable[[str], None], get_object: Callable[[str], str]
):
    from etl.sds.worker.transform_update import transform_update

    # Initial state
    n_initial_processed = 5
    initial_unprocessed_data = FATAL_SDS_RECORD_AS_JSON
    initial_processed_data = pkl_dumps_lz4(
        deque(n_initial_processed * [PROCESSED_SDS_JSON_RECORD])
    )
    put_object(key=WorkerKey.TRANSFORM, body=initial_unprocessed_data)
    put_object(key=WorkerKey.LOAD, body=initial_processed_data)

    # Execute the transform worker
    response = transform_update.handler(event={}, context=None)

    # The line number in the error changes for each example, so
    # substitute it for the value 'NUMBER'
    response["error_message"] = re.sub(
        r"Line \d{1,2}", "Line NUMBER", response["error_message"]
    )
    response["error_message"] = response["error_message"].split("\n")[:3]

    assert response == {
        "stage_name": "transform",
        "processed_records": None,
        "unprocessed_records": None,
        "error_message": [
            "The following errors were encountered",
            "  -- Error 1 (RuntimeError) --",
            "  LZ4F_decompress failed with code: ERROR_frameType_unknown",
        ],
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM).decode()
    final_processed_data: str = get_object(key=WorkerKey.LOAD)

    # Confirm that no changes were persisted
    assert final_unprocessed_data == initial_unprocessed_data
    assert final_processed_data == initial_processed_data


def test__export_events():
    org = Root.create_ods_organisation(ods_code="AAA")
    product_team = org.create_product_team(id=uuid4(), name="abc")

    devices = []
    for i in range(3):
        device = product_team.create_device(
            name=f"device-{i}", device_type=DeviceType.PRODUCT
        )
        device.add_tag(foo=str(i))
        devices.append(device)
    events = export_events(devices)
    for event in events:
        assert len(event) == 1
    event_names = [list(event.keys())[0] for event in events]
    assert event_names == [
        "device_created_event",
        "device_tag_added_event",
    ] * len(devices)
