from collections.abc import Callable
from json import JSONDecodeError
from types import FunctionType

from botocore.exceptions import ClientError
from etl.clear_state_inputs import EMPTY_JSON_DATA, EMPTY_LDIF_DATA
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from event.json import json_loads
from mypy_boto3_s3 import S3Client

from etl.sds.tests.etl_test_utils.etl_state import EtlConfig

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
    result = False

    response = s3_client.list_objects(Bucket=bucket, Prefix=key_prefix)

    for item in response.get("Contents", []):
        if item and question is not None:
            result = ask_s3(
                s3_client=s3_client, bucket=bucket, key=item["Key"], question=question
            )
    return result


def was_trigger_key_deleted(s3_client, bucket, etl_config: EtlConfig):
    return not ask_s3(
        s3_client=s3_client, bucket=bucket, key=etl_config.initial_trigger_key
    )


def was_changelog_number_updated(s3_client, bucket, new_changelog_number):
    return ask_s3(
        s3_client=s3_client,
        key=CHANGELOG_NUMBER,
        bucket=bucket,
        question=lambda x: json_loads(x) == new_changelog_number,
    )


def etl_state_is_clear(s3_client, bucket) -> bool:

    extract_is_empty = ask_s3(
        s3_client=s3_client,
        key=WorkerKey.EXTRACT,
        bucket=bucket,
        question=lambda x: x == EMPTY_LDIF_DATA,
    )
    transform_is_empty = ask_s3(
        s3_client=s3_client,
        key=WorkerKey.TRANSFORM,
        bucket=bucket,
        question=lambda x: x == EMPTY_JSON_DATA,
    )
    load_is_empty = ask_s3(
        s3_client=s3_client,
        key=WorkerKey.LOAD,
        bucket=bucket,
        question=lambda x: x == EMPTY_JSON_DATA,
    )
    print(  # noqa
        f"{{extract, transform, load}} is empty == {{{extract_is_empty, transform_is_empty, load_is_empty}}}"
    )
    return extract_is_empty and transform_is_empty and load_is_empty
