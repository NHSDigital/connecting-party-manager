from collections.abc import Callable
from json import JSONDecodeError
from types import FunctionType

from botocore.exceptions import ClientError
from etl.clear_state_inputs import EMPTY_JSON_DATA, EMPTY_LDIF_DATA
from etl.sds.tests.etl_test_utils.etl_state import EtlConfig
from etl_utils.constants import CHANGELOG_NUMBER, ETL_STATE_LOCK, WorkerKey
from event.json import json_loads
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_s3 import S3Client

ALLOWED_EXCEPTIONS = (JSONDecodeError,)


def ask_s3(
    s3_client: S3Client, bucket: str, key: str, question: Callable[[any], bool] = None
) -> bool:
    result = True
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except ClientError:
        result = False

    if result and question is not None:
        data = response["Body"].read()
        try:
            result = question(data)
        except ALLOWED_EXCEPTIONS:
            result = False
    return result


def ask_s3_prefix(
    s3_client: S3Client, bucket: str, key_prefix: str, question: FunctionType = None
):
    response = s3_client.list_objects(Bucket=bucket, Prefix=key_prefix)
    keys = [item["Key"] for item in response.get("Contents", [])]
    return any(
        ask_s3(s3_client=s3_client, bucket=bucket, key=key, question=question)
        for key in keys
    )


def was_trigger_key_deleted(s3_client, etl_config: EtlConfig):
    return not ask_s3(
        s3_client=s3_client,
        bucket=etl_config.bucket,
        key=etl_config.initial_trigger_key,
    )


def was_queue_history_created(
    s3_client, etl_config: EtlConfig, expected_content: bytes
):
    return ask_s3_prefix(
        s3_client=s3_client,
        bucket=etl_config.bucket,
        key_prefix=f"{etl_config.queue_history_key_prefix}{etl_config.etl_type}",
        question=lambda x: x == expected_content,
    )


def was_state_machine_history_created(
    s3_client, etl_config: EtlConfig, expected_content: bytes
):
    return ask_s3_prefix(
        s3_client=s3_client,
        bucket=etl_config.bucket,
        key_prefix=f"{etl_config.state_machine_history_key_prefix}{etl_config.etl_type}",
        question=lambda x: x == expected_content,
    )


def was_changelog_number_updated(s3_client, bucket, new_changelog_number):
    return ask_s3(
        s3_client=s3_client,
        key=CHANGELOG_NUMBER,
        bucket=bucket,
        question=lambda x: json_loads(x) == new_changelog_number,
    )


def extract_is_empty(s3_client, bucket) -> bool:
    return ask_s3(
        s3_client=s3_client,
        key=WorkerKey.EXTRACT,
        bucket=bucket,
        question=lambda x: x == EMPTY_LDIF_DATA,
    )


def transform_is_empty(s3_client, bucket) -> bool:
    return ask_s3(
        s3_client=s3_client,
        key=WorkerKey.TRANSFORM,
        bucket=bucket,
        question=lambda x: x == EMPTY_JSON_DATA,
    )


def load_is_empty(s3_client, bucket) -> bool:
    return ask_s3(
        s3_client=s3_client,
        key=WorkerKey.LOAD,
        bucket=bucket,
        question=lambda x: x == EMPTY_JSON_DATA,
    )


def was_etl_state_lock_removed(s3_client, bucket) -> bool:
    return ask_s3(
        s3_client=s3_client,
        key=ETL_STATE_LOCK,
        bucket=bucket,
    )


def database_isnt_empty(db_client: "DynamoDBClient", table_name: str):
    count = db_client.scan(TableName=table_name, Limit=1, Select="COUNT")["Count"]
    return count == 1
