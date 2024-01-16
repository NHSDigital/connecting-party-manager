import json
from datetime import datetime as dt
from functools import cache

import boto3
import pytest
from etl_utils.constants import WorkerKey
from event.json import json_loads

from test_helpers.terraform import read_terraform_output

NAME_SEPARATOR = "."
BAD_CHARACTERS = [" ", ":"]


@pytest.fixture
def state_machine_input(request: pytest.FixtureRequest):
    return execute_state_machine(**request.param)


@pytest.fixture
def worker_data(request: pytest.FixtureRequest):
    client = boto3.client("s3")
    etl_bucket = read_terraform_output("sds_etl.value.bucket")

    for key in WorkerKey._member_names_:
        _data = request.param.get(key.lower(), "")
        client.put_object(
            Bucket=etl_bucket, Key=WorkerKey._member_map_[key], Body=_data
        )


def _execution_name(state_machine_input):
    params = NAME_SEPARATOR.join(map(str, state_machine_input.values()))
    date_str = str(dt.now())
    name = f"{params}{NAME_SEPARATOR}{date_str}"
    for char in BAD_CHARACTERS:
        name = name.replace(char, NAME_SEPARATOR)
    return name


@cache
def execute_state_machine(**state_machine_input):
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
    return state_machine_input


def get_changelog_number_from_s3() -> str:
    client = boto3.client("s3")
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    changelog_key = read_terraform_output("sds_etl.value.changelog_key")
    response = client.get_object(Bucket=etl_bucket, Key=changelog_key)
    return json_loads(response["Body"].read())


@pytest.mark.integration
@pytest.mark.parametrize(
    "worker_data",
    [
        {},  # no initial worker data
    ],
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
