import json
import time
from collections import deque

import boto3
import pytest
from botocore.config import Config
from domain.core.device import DeviceType
from domain.core.device_key import DeviceKeyType
from domain.core.enum import Status
from etl.clear_state_inputs import EMPTY_JSON_DATA, EMPTY_LDIF_DATA
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from etl_utils.trigger.model import StateMachineInput
from event.aws.client import dynamodb_client
from event.json import json_loads
from mypy_boto3_stepfunctions.type_defs import StartSyncExecutionOutputTypeDef

from etl.sds.tests.constants import BULK_TEST_CHANGELOG_NUMBER, EtlTestDataPath
from etl.sds.worker.extract.tests.test_extract_worker import (
    ANOTHER_GOOD_SDS_RECORD,
    GOOD_SDS_RECORD,
)
from etl.sds.worker.load_bulk.tests._test_load_bulk_worker import MockDeviceRepository
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.pytest_skips import long_running
from test_helpers.terraform import read_terraform_output

# Configure the boto3 retry settings
config = Config(retries={"max_attempts": 10, "mode": "standard"})

# Note that unique identifier "000428682512" is the identifier of 'GOOD_SDS_RECORD'
DELETION_REQUEST_000428682512 = """
dn: o=nhs,ou=Services,uniqueIdentifier=000428682512
changetype: delete
objectclass: delete
uniqueidentifier: 000428682512
"""

DELETION_REQUEST_000842065542 = """
dn: o=nhs,ou=Services,uniqueIdentifier=000842065542
changetype: delete
objectclass: delete
uniqueidentifier: 000842065542
"""


@pytest.fixture
def step_functions_client():
    return boto3.client("stepfunctions", config=config)


@pytest.fixture
def s3_client():
    return boto3.client("s3")


@pytest.fixture
def state_machine_input(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def worker_data(request: pytest.FixtureRequest, s3_client):
    etl_bucket = read_terraform_output("sds_etl.value.bucket")

    for key, data in request.param.items():
        s3_client.put_object(Bucket=etl_bucket, Key=key, Body=data)
    return request.param


@pytest.fixture
def repository():
    client = dynamodb_client()
    table_name = read_terraform_output("dynamodb_table_name.value")
    clear_dynamodb_table(client=client, table_name=table_name)
    return MockDeviceRepository(table_name=table_name, dynamodb_client=client)


def execute_state_machine(
    state_machine_input: StateMachineInput, step_functions_client
) -> StartSyncExecutionOutputTypeDef:
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    name = state_machine_input.name
    execution_response = step_functions_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=name,
        input=json.dumps(state_machine_input.dict()),
    )

    status = "RUNNING"
    while status == "RUNNING":
        response = step_functions_client.describe_execution(
            executionArn=execution_response["executionArn"]
        )
        status = response["status"]

    if response["status"] != "SUCCEEDED":
        try:
            cause = json_loads(response["cause"])
            error_message = cause["errorMessage"]
            stack_trace = cause["stackTrace"]
        except Exception:
            error_message = response.get("cause", "no error message")
            stack_trace = []

        print(  # noqa: T201
            "Error captured from state machine:\n",
            error_message,
            "\n",
            *stack_trace,
        )
        raise RuntimeError(response.get("error", "no error message"))
    return response


def get_changelog_number_from_s3(s3_client) -> str:
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    changelog_key = read_terraform_output("sds_etl.value.changelog_key")
    response = s3_client.get_object(Bucket=etl_bucket, Key=changelog_key)
    return json_loads(response["Body"].read())


def get_object(s3_client, key: WorkerKey) -> str:
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    response = s3_client.get_object(Bucket=etl_bucket, Key=key)
    return response["Body"].read()


def put_object(s3_client, key: WorkerKey, body: bytes) -> str:
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    return s3_client.put_object(Bucket=etl_bucket, Key=key, Body=body)


@pytest.mark.integration
@pytest.mark.parametrize(
    "state_machine_input",
    [StateMachineInput.update(changelog_number_start=1, changelog_number_end=1)],
    indirect=True,
)
def test_changelog_number_update(
    state_machine_input: StateMachineInput, step_functions_client, s3_client
):
    execute_state_machine(state_machine_input, step_functions_client)
    changelog_number_from_s3 = get_changelog_number_from_s3(s3_client)
    assert changelog_number_from_s3 == state_machine_input.changelog_number_end


@pytest.mark.integration
@pytest.mark.parametrize(
    "worker_data",
    [
        {
            WorkerKey.EXTRACT: "\n".join([GOOD_SDS_RECORD, ANOTHER_GOOD_SDS_RECORD]),
            WorkerKey.TRANSFORM: pkl_dumps_lz4(deque()),
            WorkerKey.LOAD: pkl_dumps_lz4(deque()),
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "state_machine_input",
    [
        StateMachineInput.bulk(changelog_number=123),
    ],
    indirect=True,
)
def test_end_to_end(
    repository: MockDeviceRepository,
    worker_data,
    s3_client,
    state_machine_input,
    step_functions_client,
):
    execute_state_machine(state_machine_input, step_functions_client)

    extract_data = get_object(s3_client, key=WorkerKey.EXTRACT)
    transform_data = pkl_loads_lz4(get_object(s3_client, key=WorkerKey.TRANSFORM))
    load_data = pkl_loads_lz4(get_object(s3_client, key=WorkerKey.LOAD))

    assert len(extract_data) == 0
    assert len(transform_data) == 0
    assert len(load_data) == 0
    assert len(list(repository.all_devices())) == len(
        worker_data[WorkerKey.EXTRACT].split("\n\n")
    )


def _wait_until_empty(get_data_fn, sleep_time_seconds=15):
    time.sleep(sleep_time_seconds)
    data = get_data_fn()
    while len(data) > 0:
        time.sleep(sleep_time_seconds)
        data = get_data_fn()


@long_running
@pytest.mark.integration
def test_end_to_end_bulk_trigger(repository: MockDeviceRepository, s3_client):
    bucket = read_terraform_output("sds_etl.value.bucket")
    test_data_bucket = read_terraform_output("test_data_bucket.value")
    bulk_trigger_prefix = read_terraform_output("sds_etl.value.bulk_trigger_prefix")
    initial_trigger_key = f"{bulk_trigger_prefix}/{BULK_TEST_CHANGELOG_NUMBER}.ldif"

    # Clear/set the initial state
    s3_client.put_object(Bucket=bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA)
    s3_client.put_object(Bucket=bucket, Key=WorkerKey.TRANSFORM, Body=EMPTY_JSON_DATA)
    s3_client.put_object(Bucket=bucket, Key=WorkerKey.LOAD, Body=EMPTY_JSON_DATA)
    s3_client.delete_object(Bucket=bucket, Key=CHANGELOG_NUMBER)

    product_count = repository.count(by=DeviceType.PRODUCT)
    assert product_count == 0

    endpoint_count = repository.count(by=DeviceType.ENDPOINT)
    assert endpoint_count == 0

    # Trigger the bulk load
    s3_client.copy_object(
        Bucket=bucket,
        Key=initial_trigger_key,
        CopySource={"Bucket": test_data_bucket, "Key": EtlTestDataPath.FULL_LDIF},
    )

    _wait_until_empty(
        lambda: get_object(s3_client, key=WorkerKey.EXTRACT),
    )
    _wait_until_empty(
        lambda: pkl_loads_lz4(get_object(s3_client, key=WorkerKey.TRANSFORM)),
    )
    _wait_until_empty(
        lambda: pkl_loads_lz4(get_object(s3_client, key=WorkerKey.LOAD)),
    )

    product_count = repository.count(by=DeviceType.PRODUCT)
    endpoint_count = repository.count(by=DeviceType.ENDPOINT)

    accredited_system_count = repository.count(by=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    message_handling_system_count = repository.count(
        by=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )

    assert product_count == accredited_system_count == 5670
    assert endpoint_count == message_handling_system_count == 154506


@pytest.mark.integration
@pytest.mark.parametrize(
    "worker_data",
    [
        {
            WorkerKey.EXTRACT: "\n".join([GOOD_SDS_RECORD, ANOTHER_GOOD_SDS_RECORD]),
            WorkerKey.TRANSFORM: pkl_dumps_lz4(deque()),
            WorkerKey.LOAD: pkl_dumps_lz4(deque()),
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "state_machine_input",
    [StateMachineInput.bulk(changelog_number=123)],
    indirect=True,
)
def test_end_to_end_changelog_delete(
    repository: MockDeviceRepository,
    worker_data,
    step_functions_client,
    s3_client,
    state_machine_input,
):
    """Note that the start of this test is the same as test_end_to_end, and then makes changes"""
    execute_state_machine(state_machine_input, step_functions_client)

    extract_data = get_object(s3_client, key=WorkerKey.EXTRACT)
    transform_data = pkl_loads_lz4(get_object(s3_client, key=WorkerKey.TRANSFORM))
    load_data = pkl_loads_lz4(get_object(s3_client, key=WorkerKey.LOAD))

    assert len(extract_data) == 0
    assert len(transform_data) == 0
    assert len(load_data) == 0
    assert len(list(repository.all_devices())) == len(
        worker_data[WorkerKey.EXTRACT].split("\n\n")
    )

    # Get the id of the device with unique id 000428682512
    (device_000428682512,) = repository.query_by_tag(unique_identifier="000428682512")

    # Now execute a changelog initial state in the ETL
    put_object(s3_client, key=WorkerKey.EXTRACT, body=DELETION_REQUEST_000428682512)
    response = execute_state_machine(
        state_machine_input=StateMachineInput.update(
            changelog_number_start=124, changelog_number_end=125
        ),
        step_functions_client=step_functions_client,
    )
    assert response["status"] == "SUCCEEDED"

    # Verify that the device with unique id 000428682512 is now "inactive"
    _device_000428682512 = repository.read_inactive(device_000428682512.id)
    assert _device_000428682512.status == Status.INACTIVE

    # Verify that the other device is still "active"
    (device_000842065542,) = repository.query_by_tag(unique_identifier="000842065542")
    assert device_000842065542.status == Status.ACTIVE

    # Execute another changelog initial state in the ETL
    put_object(s3_client, key=WorkerKey.EXTRACT, body=DELETION_REQUEST_000842065542)
    response = execute_state_machine(
        state_machine_input=StateMachineInput.update(
            changelog_number_start=124, changelog_number_end=125
        ),
        step_functions_client=step_functions_client,
    )
    assert response["status"] == "SUCCEEDED"

    # Verify that the device with unique id 000428682512 is still "inactive"
    __device_000428682512 = repository.read_inactive(_device_000428682512.id)
    assert __device_000428682512.status == Status.INACTIVE

    # Verify that the other device is now "inactive"
    _device_000842065542 = repository.read_inactive(device_000842065542.id)
    assert _device_000842065542.status == Status.INACTIVE

    # Verify that inactive devices cannot be queried by tag
    assert repository.query_by_tag(unique_identifier="000842065542") == []
    assert repository.query_by_tag(unique_identifier="000842065542") == []
