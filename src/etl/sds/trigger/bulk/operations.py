import hashlib
import json
from collections import deque
from http import HTTPStatus
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.trigger.model import StateMachineInput
from event.json import json_loads

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_stepfunctions import SFNClient

EMPTY_LDIF = ""
EMPTY_JSON_ARRAY = deque()


class StateFileNotEmpty(Exception):
    def __init__(self, bucket, key, content):
        super().__init__(
            self,
            f"Expected empty data '{content}' in s3://{bucket}/{key}",
        )


class TableNotEmpty(Exception):
    def __init__(self, table_name: str):
        super().__init__(self, f"Expected empty table '{table_name}'")


class ChangelogNumberExists(Exception):
    def __init__(self, bucket, key):
        super().__init__(
            self, f"s3://{bucket}/{key} should not exist when using bulk trigger"
        )


def _object_exists(s3_client: "S3Client", bucket: str, key: str) -> str:
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as error:
        if error.response["Error"]["Code"] != str(HTTPStatus.NOT_FOUND):
            raise error
        file_hash = None
    else:
        file_hash = json_loads(response["ETag"])
    return file_hash


def validate_no_changelog_number(s3_client: "S3Client", source_bucket):
    if _object_exists(s3_client=s3_client, bucket=source_bucket, key=CHANGELOG_NUMBER):
        raise ChangelogNumberExists(bucket=source_bucket, key=CHANGELOG_NUMBER)


def _validate_s3_file_content(
    s3_client: "S3Client", source_bucket: str, key: WorkerKey, content: bytes
):
    s3_file_hash = _object_exists(s3_client=s3_client, bucket=source_bucket, key=key)
    expected_file_hash = hashlib.md5(content).hexdigest()
    if s3_file_hash and (s3_file_hash != expected_file_hash):
        raise StateFileNotEmpty(bucket=source_bucket, key=key, content=content)


def validate_state_keys_are_empty(s3_client: "S3Client", source_bucket):
    for key, content in (
        (WorkerKey.EXTRACT, EMPTY_LDIF.encode()),
        (WorkerKey.TRANSFORM, pkl_dumps_lz4(EMPTY_JSON_ARRAY)),
        (WorkerKey.LOAD, pkl_dumps_lz4(EMPTY_JSON_ARRAY)),
    ):
        _validate_s3_file_content(
            s3_client=s3_client, source_bucket=source_bucket, key=key, content=content
        )


def validate_database_is_empty(dynamodb_client: "DynamoDBClient", table_name: str):
    response = dynamodb_client.scan(TableName=table_name, Limit=1, Select="COUNT")
    if response["Count"] > 0:
        raise TableNotEmpty(table_name=table_name)


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
