import json
import os
import re
from typing import Callable
from unittest import mock

import pytest
from etl_utils.constants import WorkerKey
from event.json import json_loads
from moto import mock_aws
from mypy_boto3_s3 import S3Client

LDIF_RECORD_DELIMITER = "\n\n"
BUCKET_NAME = "my-bucket"

GOOD_SDS_RECORD = """
dn: uniqueIdentifier=000428682512,ou=Services,o=nhs
objectClass: nhsAS
objectClass: top
nhsApproverURP: uniqueIdentifier=562983788547,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs
nhsAsClient: RVL
nhsAsSvcIA: urn:nhs:names:services:pds:QUPA_IN040000UK01
nhsDateApproved: 20090601140104
nhsDateRequested: 20090601135904
nhsIDCode: RVL
nhsMhsManufacturerOrg: LSP04
nhsMHSPartyKey: RVL-806539
nhsProductKey: 634
nhsProductName: Cerner Millennium
nhsProductVersion: 2005.02
nhsRequestorURP: uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs
nhsTempUid: 9713
uniqueIdentifier: 000428682512
"""

# Bad because fields are missing (fails domain)
BAD_SDS_RECORD = """
dn: uniqueIdentifier=000428682512,ou=Services,o=nhs
objectClass: nhsAS
objectClass: top
"""

# Fatal because DN is missing (fails LDIF parsing)
FATAL_SDS_RECORD = """
objectClass: nhsAS
objectClass: foo
"""

PROCESSED_SDS_RECORD = {}  # Empty dict as a dummy value, doesn't matter for extract


@pytest.fixture(scope="session")
def mock_s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ,
        {"ETL_BUCKET": BUCKET_NAME, "AWS_DEFAULT_REGION": "us-east-1"},
        clear=True,
    ):
        from etl.sds.worker.extract import extract

        extract.CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield extract.CLIENT


@pytest.fixture
def put_object(mock_s3_client: S3Client):
    return lambda key, body: (
        mock_s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=body)
    )


@pytest.fixture
def get_object(mock_s3_client: S3Client):
    return lambda key: (
        mock_s3_client.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read().decode()
    )


def _split_ldif(data: str) -> list[str]:
    return list(filter(bool, data.split(LDIF_RECORD_DELIMITER)))


@pytest.mark.parametrize(
    ("initial_unprocessed_data", "initial_processed_data"),
    [
        ("", json.dumps([PROCESSED_SDS_RECORD] * 10)),
        ("\n".join([GOOD_SDS_RECORD] * 5), json.dumps([PROCESSED_SDS_RECORD] * 5)),
        ("\n".join([GOOD_SDS_RECORD] * 10), "[]"),
    ],
    ids=["processed-only", "partly-processed", "unprocessed-only"],
)
def test_extract_worker_pass(
    initial_unprocessed_data: str,
    initial_processed_data: str,
    put_object: Callable[[str], None],
    get_object: Callable[[str], str],
):
    from etl.sds.worker.extract import extract

    # Initial state
    n_initial_unprocessed = len(_split_ldif(initial_unprocessed_data))
    n_initial_processed = len(json_loads(initial_processed_data))
    put_object(key=WorkerKey.EXTRACT, body=initial_unprocessed_data)
    put_object(key=WorkerKey.TRANSFORM, body=initial_processed_data)

    # Execute the extract worker
    response = extract.handler(event=None, context=None)
    assert response == {
        "stage_name": "extract",
        "processed_records": 10,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.EXTRACT)
    final_processed_data: str = get_object(key=WorkerKey.TRANSFORM)
    n_final_unprocessed = len(_split_ldif(final_unprocessed_data))
    n_final_processed = len(json_loads(final_processed_data))

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert n_final_processed == n_initial_unprocessed + n_initial_processed
    assert n_final_unprocessed == 0


@pytest.mark.parametrize(
    ("initial_unprocessed_data", "expected_extra_processed_records"),
    [
        (
            "\n".join([BAD_SDS_RECORD, GOOD_SDS_RECORD, GOOD_SDS_RECORD]),
            0,
        ),
        (
            "\n".join([GOOD_SDS_RECORD, BAD_SDS_RECORD, GOOD_SDS_RECORD]),
            1,
        ),
        (
            "\n".join([GOOD_SDS_RECORD, GOOD_SDS_RECORD, BAD_SDS_RECORD]),
            2,
        ),
    ],
    ids=["first-record-bad", "second-record-bad", "third-record-bad"],
)
def test_extract_worker_bad_record(
    initial_unprocessed_data: str,
    expected_extra_processed_records: int,
    put_object: Callable[[str], None],
    get_object: Callable[[str], str],
):
    from etl.sds.worker.extract import extract

    # Initial state
    n_initial_processed = 5
    n_initial_unprocessed = len(_split_ldif(initial_unprocessed_data))
    initial_processed_data = json.dumps(n_initial_processed * [PROCESSED_SDS_RECORD])
    put_object(key=WorkerKey.EXTRACT, body=initial_unprocessed_data)
    put_object(key=WorkerKey.TRANSFORM, body=initial_processed_data)

    # Execute the extract worker
    response = extract.handler(event=None, context=None)
    assert response == {
        "stage_name": "extract",
        "processed_records": n_initial_processed + expected_extra_processed_records,
        "unprocessed_records": n_initial_unprocessed - expected_extra_processed_records,
        "error_message": (
            "The following errors were encountered\n"
            "  -- Error 1 --\n"
            f"  Failed to parse record {expected_extra_processed_records}\n"
            "  {'objectclass': ['nhsAS', 'top']}\n"
            "  9 validation errors for NhsAccreditedSystem\n"
            "  uniqueidentifier\n"
            "    field required (type=value_error.missing)\n"
            "  nhsapproverurp\n"
            "    field required (type=value_error.missing)\n"
            "  nhsdateapproved\n"
            "    field required (type=value_error.missing)\n"
            "  nhsrequestorurp\n"
            "    field required (type=value_error.missing)\n"
            "  nhsdaterequested\n"
            "    field required (type=value_error.missing)\n"
            "  nhsidcode\n"
            "    field required (type=value_error.missing)\n"
            "  nhsmhspartykey\n"
            "    field required (type=value_error.missing)\n"
            "  nhsproductkey\n"
            "    field required (type=value_error.missing)\n"
            "  nhsassvcia\n"
            "    field required (type=value_error.missing)"
        ),
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.EXTRACT)
    final_processed_data: str = get_object(key=WorkerKey.TRANSFORM)
    n_final_unprocessed = len(_split_ldif(final_unprocessed_data))
    n_final_processed = len(json_loads(final_processed_data))

    # Confirm that there are still unprocessed records, and that there may have been
    # some records processed successfully
    assert n_final_unprocessed > 0
    assert n_final_processed == n_initial_processed + expected_extra_processed_records
    assert (
        n_final_unprocessed == n_initial_unprocessed - expected_extra_processed_records
    )


@pytest.mark.parametrize(
    "initial_unprocessed_data",
    [
        "\n".join([FATAL_SDS_RECORD, GOOD_SDS_RECORD, GOOD_SDS_RECORD]),
        "\n".join([GOOD_SDS_RECORD, FATAL_SDS_RECORD, GOOD_SDS_RECORD]),
        "\n".join([GOOD_SDS_RECORD, GOOD_SDS_RECORD, FATAL_SDS_RECORD]),
    ],
    ids=["first-record-bad", "second-record-bad", "third-record-bad"],
)
def test_extract_worker_fatal_record(
    initial_unprocessed_data: str,
    put_object: Callable[[str], None],
    get_object: Callable[[str], str],
):
    from etl.sds.worker.extract import extract

    # Initial state
    _split_data = _split_ldif(initial_unprocessed_data)
    n_initial_unprocessed = len(_split_data)
    n_initial_processed = 5
    initial_processed_data = json.dumps(n_initial_processed * [PROCESSED_SDS_RECORD])
    put_object(key=WorkerKey.EXTRACT, body=initial_unprocessed_data)
    put_object(key=WorkerKey.TRANSFORM, body=initial_processed_data)

    # Execute the extract worker
    response = extract.handler(event=None, context=None)

    # The line number in the error changes for each example, so
    # substitute it for the value 'NUMBER'
    response["error_message"] = re.sub(
        "Line \d{1,2}", "Line NUMBER", response["error_message"]
    )

    assert response == {
        "stage_name": "extract",
        "processed_records": None,
        "unprocessed_records": None,
        "error_message": (
            "The following errors were encountered\n"
            "  -- Error 1 --\n"
            '  Line NUMBER: First line of record does not start with "dn:": '
            "'objectclass'"
        ),
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.EXTRACT)
    final_processed_data: str = get_object(key=WorkerKey.TRANSFORM)
    n_final_unprocessed = len(_split_ldif(final_unprocessed_data))
    n_final_processed = len(json_loads(final_processed_data))

    # Confirm that no changes were persisted
    assert n_final_unprocessed == n_initial_unprocessed
    assert n_final_processed == n_initial_processed
