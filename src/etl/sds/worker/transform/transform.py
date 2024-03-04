from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.json import json_dump_bytes
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEnvironment
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from event.json import json_load
from sds.cpm_translation import translate

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


S3_CLIENT = boto3.client("s3")
DYNAMODB_CLIENT = dynamodb_client()
ENVIRONMENT = WorkerEnvironment.build()


def transform(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str
) -> WorkerActionResponse:
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records = deque(json_load(f))

    with smart_open(s3_path=s3_output_path, s3_client=s3_client) as f:
        processed_records: list[dict] = json_load(f)

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: translate(record),
    )

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        exception=exception,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
    )


def handler(event, context):
    response = execute_step_chain(
        action=transform,
        s3_client=S3_CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.TRANSFORM),
        s3_output_path=ENVIRONMENT.s3_path(WorkerKey.LOAD),
        unprocessed_dumper=json_dump_bytes,
        processed_dumper=json_dump_bytes,
    )
    return asdict(response)
