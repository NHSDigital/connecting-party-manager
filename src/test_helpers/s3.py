from collections import deque
from json import JSONDecodeError
from types import FunctionType

from botocore.exceptions import ClientError
from etl_utils.constants import ETL_QUEUE_HISTORY, ETL_STATE_MACHINE_HISTORY, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from mypy_boto3_s3 import S3Client

from test_helpers.terraform import read_terraform_output

TEST_DATA_NAME = "123.ldif"
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()
ALLOWED_EXCEPTIONS = (JSONDecodeError,)


def _ask_s3(s3_client: S3Client, bucket: str, key: str, question: FunctionType = None):
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


def _ask_s3_prefix(
    s3_client: S3Client, bucket: str, key_prefix: str, question: FunctionType = None
):
    result = False

    response = s3_client.list_objects(Bucket=bucket, Prefix=key_prefix)

    for item in response.get("Contents", []):
        if item and question is not None:
            result = _ask_s3(
                s3_client=s3_client, bucket=bucket, key=item["Key"], question=question
            )
    return result


def _set_etl_content_config():
    bulk_trigger_prefix = read_terraform_output("sds_etl.value.bulk_trigger_prefix")
    return {
        "etl_bucket": read_terraform_output("sds_etl.value.bucket"),
        "bulk_trigger_prefix": bulk_trigger_prefix,
        "initial_trigger_key": f"{bulk_trigger_prefix}/{TEST_DATA_NAME}",
        "queue_history_key_prefix": ETL_QUEUE_HISTORY,
        "state_machine_history_key_prefix": ETL_STATE_MACHINE_HISTORY,
        "table_name": read_terraform_output("dynamodb_table_name.value"),
    }


def _set_etl_content(s3_client: S3Client, bucket_config: dict, bulk: bool = False):
    queue_history_key_prefix = (
        f"{bucket_config['queue_history_key_prefix']}/bulk"
        if bulk
        else bucket_config["queue_history_key_prefix"]
    )
    state_machine_history_key_prefix = (
        f"{bucket_config['state_machine_history_key_prefix']}/bulk"
        if bulk
        else bucket_config["state_machine_history_key_prefix"]
    )

    #     # Clear/set the initial state
    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"], Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA
    )
    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"],
        Key=WorkerKey.TRANSFORM,
        Body=pkl_dumps_lz4(EMPTY_JSON_DATA),
    )
    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"],
        Key=WorkerKey.LOAD,
        Body=pkl_dumps_lz4(EMPTY_JSON_DATA),
    )
    s3_client.delete_object(
        Bucket=bucket_config["etl_bucket"], Key=bucket_config["initial_trigger_key"]
    )
    queue_history_files = s3_client.list_objects(
        Bucket=bucket_config["etl_bucket"], Prefix=queue_history_key_prefix
    )
    for item in queue_history_files.get("Contents", []):
        s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=item["Key"])
    state_machine_history_files = s3_client.list_objects(
        Bucket=bucket_config["etl_bucket"], Prefix=state_machine_history_key_prefix
    )
    for item in state_machine_history_files.get("Contents", []):
        s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=item["Key"])
