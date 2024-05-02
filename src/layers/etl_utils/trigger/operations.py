import json
from typing import TYPE_CHECKING

from etl_utils.constants import EMPTY_ARRAY, EMPTY_LDIF, WorkerKey
from etl_utils.io import pkl_dumps_lz4

from .model import StateMachineInput

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_stepfunctions import SFNClient

NOT_FOUND_CODE = "NoSuchKey"


class StateFileNotEmpty(Exception):
    def __init__(self, bucket, key, content):
        super().__init__(
            self,
            f"Expected empty data '{content}' in s3://{bucket}/{key}",
        )


def start_execution(
    step_functions_client: "SFNClient",
    state_machine_arn: str,
    state_machine_input: StateMachineInput,
):
    return step_functions_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=state_machine_input.name,
        input=json.dumps(state_machine_input.dict()),
    )


def object_exists(s3_client: "S3Client", bucket: str, key: str) -> str:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except Exception as error:
        if error.response["Error"]["Code"] != NOT_FOUND_CODE:
            raise error
        file_hash = None
    else:
        file_hash = response["Body"].read()
    return file_hash


def _validate_s3_file_content(
    s3_client: "S3Client", source_bucket: str, key: WorkerKey, content: bytes
):
    s3_file_hash = object_exists(s3_client=s3_client, bucket=source_bucket, key=key)
    if s3_file_hash and (s3_file_hash != content):
        raise StateFileNotEmpty(bucket=source_bucket, key=key, content=content)


def validate_state_keys_are_empty(s3_client: "S3Client", bucket):
    for key, content in (
        (WorkerKey.EXTRACT, EMPTY_LDIF.encode()),
        (WorkerKey.TRANSFORM, pkl_dumps_lz4(EMPTY_ARRAY)),
        (WorkerKey.LOAD, pkl_dumps_lz4(EMPTY_ARRAY)),
    ):
        _validate_s3_file_content(
            s3_client=s3_client, source_bucket=bucket, key=key, content=content
        )
