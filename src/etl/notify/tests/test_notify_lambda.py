import json

import boto3
import pytest

from test_helpers.terraform import read_terraform_output

STATE_MACHINE_INPUT_WITHOUT_ERROR_MESSAGE = [
    {
        "ETag": '"xxx"',
        "ServerSideEncryption": "AES256",
        "VersionId": "VHBhCwygSeYxgEEecU7N.meZl3uKDoaA",
    },
    {
        "stage_name": "load",
        "processed_records": 0,
        "unprocessed_records": 0,
        "error_message": None,
    },
]

STATE_MACHINE_INPUT_WITH_ERROR_MESSAGE = [
    {
        "ETag": '"xxx"',
        "ServerSideEncryption": "AES256",
        "VersionId": "VHBhCwygSeYxgEEecU7N.meZl3uKDoaA",
    },
    {
        "stage_name": "load",
        "processed_records": 0,
        "unprocessed_records": 0,
        "error_message": "oops",
    },
]


def test_notify_lambda_with_state_machine_input_without_error_message():
    from etl.notify import notify

    assert notify.handler(event=STATE_MACHINE_INPUT_WITHOUT_ERROR_MESSAGE) == "pass"


def test_notify_lambda_with_state_machine_input_with_error_message():
    from etl.notify import notify

    assert notify.handler(event=STATE_MACHINE_INPUT_WITH_ERROR_MESSAGE) == "fail"


@pytest.mark.integration
def test_notify_lambda_without_error_message():
    notify_lambda_arn = read_terraform_output("sds_etl.value.notify_lambda_arn")

    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName=notify_lambda_arn,
        Payload=json.dumps([{"message": "test"}]).encode(),
    )
    decoded_payload = response["Payload"].read().decode("utf-8")
    decoded_payload = decoded_payload.strip('"')
    assert decoded_payload == "pass"


@pytest.mark.integration
def test_notify_lambda_with_error_message():
    notify_lambda_arn = read_terraform_output("sds_etl.value.notify_lambda_arn")

    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName=notify_lambda_arn,
        Payload=json.dumps(
            [
                {
                    "message": "test",
                    "error_message": "this is an error",
                }
            ]
        ).encode(),
    )
    decoded_payload = response["Payload"].read().decode("utf-8")
    decoded_payload = decoded_payload.strip('"')
    assert decoded_payload == "fail"
