import json
from datetime import datetime as dt
from functools import cache

import boto3
import pytest
from etl_utils.constants import WorkerKey
from event.json import json_loads
from mypy_boto3_stepfunctions.type_defs import StartSyncExecutionOutputTypeDef

from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from test_helpers.terraform import read_terraform_output

NAME_SEPARATOR = "."
BAD_CHARACTERS = [" ", ":"]
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


@pytest.fixture
def state_machine_input(request: pytest.FixtureRequest):
    execute_state_machine(**request.param)
    return request.param


@pytest.fixture
def worker_data(request: pytest.FixtureRequest):
    client = boto3.client("s3")
    etl_bucket = read_terraform_output("sds_etl.value.bucket")

    for key, data in request.param.items():
        client.put_object(Bucket=etl_bucket, Key=key, Body=data)


def _execution_name(state_machine_input):
    params = NAME_SEPARATOR.join(map(str, state_machine_input.values()))
    date_str = str(dt.now())
    name = f"{params}{NAME_SEPARATOR}{date_str}"
    for char in BAD_CHARACTERS:
        name = name.replace(char, NAME_SEPARATOR)
    return name


@cache
def execute_state_machine(**state_machine_input) -> StartSyncExecutionOutputTypeDef:
    client = boto3.client("stepfunctions")
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    name = _execution_name(state_machine_input)
    response = client.start_sync_execution(
        stateMachineArn=state_machine_arn,
        name=name,
        input=json.dumps(state_machine_input),
    )
    if response["status"] != "SUCCEEDED":
        cause = json_loads(response["cause"])
        stack_trace = cause["stackTrace"]
        print(  # noqa: T201
            "Error captured from state machine:\n",
            cause["errorMessage"],
            "\n",
            *stack_trace,
        )
        raise RuntimeError(response["error"])
    return response


def get_changelog_number_from_s3() -> str:
    client = boto3.client("s3")
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    changelog_key = read_terraform_output("sds_etl.value.changelog_key")
    response = client.get_object(Bucket=etl_bucket, Key=changelog_key)
    return json_loads(response["Body"].read())


def get_object(key: WorkerKey) -> str:
    client = boto3.client("s3")
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    response = client.get_object(Bucket=etl_bucket, Key=key)
    return response["Body"].read()


@pytest.mark.integration
@pytest.mark.parametrize(
    "worker_data",
    [{WorkerKey.EXTRACT: "", WorkerKey.TRANSFORM: "{}"}],  # empty
    indirect=True,
)
@pytest.mark.parametrize(
    "state_machine_input",
    [
        {
            "init": "extract",
            "changelog-number": 123,
        },
        {
            "init": "extract",
            "changelog-number": "abc",
        },
    ],
    indirect=True,
)
def test_changelog_number_update(worker_data, state_machine_input):
    changelog_number_from_s3 = get_changelog_number_from_s3()
    assert changelog_number_from_s3 == state_machine_input["changelog-number"]


@pytest.mark.integration
@pytest.mark.parametrize(
    "worker_data",
    [
        {
            WorkerKey.EXTRACT: "\n".join([GOOD_SDS_RECORD] * 10),
            WorkerKey.TRANSFORM: json.dumps([GOOD_SDS_RECORD_AS_JSON] * 5),
        }
    ],
    indirect=True,
    ids=["10-unprocessed-and-5-processed"],
)
@pytest.mark.parametrize(
    "state_machine_input",
    [{"init": "extract", "changelog-number": 345}],
    indirect=True,
)
def test_extract_worker(worker_data, state_machine_input):
    extract_data = get_object(key=WorkerKey.EXTRACT)
    transform_data = json_loads(get_object(key=WorkerKey.TRANSFORM))

    assert len(extract_data) == 0
    assert transform_data == [GOOD_SDS_RECORD_AS_JSON] * 15
