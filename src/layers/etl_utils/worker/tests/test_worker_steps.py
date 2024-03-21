import os
from unittest import mock

import boto3
import pytest
from etl_utils.io import pkl_dump_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from etl_utils.worker.model import WorkerActionResponse
from etl_utils.worker.steps import (
    execute_action,
    save_processed_records,
    save_unprocessed_records,
)
from event.step_chain import StepChain
from moto import mock_aws


class MyException(Exception):
    pass


BUCKET_NAME = "my-bucket"
S3_INPUT_PATH = f"s3://{BUCKET_NAME}/an_input_path"
S3_OUTPUT_PATH = f"s3://{BUCKET_NAME}/an_output_path"


def test_execute_action_pass():
    def action(**kwargs):
        return kwargs

    action_response = execute_action(
        data={
            StepChain.INIT: (action, "a_client", S3_INPUT_PATH, S3_OUTPUT_PATH, {}),
        },
        cache=None,
    )

    assert action_response == {
        "s3_client": "a_client",
        "s3_input_path": S3_INPUT_PATH,
        "s3_output_path": S3_OUTPUT_PATH,
    }


def test_execute_action_fail():
    my_exception = MyException()

    def action(**kwargs):
        raise my_exception

    with pytest.raises(MyException):
        execute_action(
            data={
                StepChain.INIT: (action, "a_client", S3_INPUT_PATH, S3_OUTPUT_PATH, {}),
            },
            cache=None,
        )


def test_save_unprocessed_records():
    data = [{"foo": "FOO"}, {"bar": "BAR"}]

    action_response = WorkerActionResponse(
        unprocessed_records=data,
        processed_records=None,
        exception=None,
        s3_input_path=S3_INPUT_PATH,
        s3_output_path=S3_OUTPUT_PATH,
    )

    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=BUCKET_NAME)

        save_unprocessed_records(
            data={
                StepChain.INIT: (action_response, s3_client, pkl_dump_lz4, None),
            },
            cache=None,
        )

        saved_data = pkl_loads_lz4(
            s3_client.get_object(Bucket=BUCKET_NAME, Key="an_input_path")["Body"].read()
        )

        assert saved_data == data


def test_save_processed_records():
    data = [{"foo": "FOO"}, {"bar": "BAR"}]

    action_response = WorkerActionResponse(
        unprocessed_records=None,
        processed_records=data,
        exception=None,
        s3_input_path=S3_INPUT_PATH,
        s3_output_path=S3_OUTPUT_PATH,
    )

    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=BUCKET_NAME)

        save_processed_records(
            data={
                StepChain.INIT: (action_response, s3_client, None, pkl_dump_lz4),
            },
            cache=None,
        )

        saved_data = pkl_loads_lz4(
            s3_client.get_object(Bucket=BUCKET_NAME, Key="an_output_path")[
                "Body"
            ].read()
        )

        assert saved_data == data
