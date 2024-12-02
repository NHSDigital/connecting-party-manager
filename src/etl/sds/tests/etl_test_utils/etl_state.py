from collections import deque
from dataclasses import dataclass

from etl_utils.constants import ETL_QUEUE_HISTORY, ETL_STATE_MACHINE_HISTORY, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from mypy_boto3_s3 import S3Client
from sds.epr.bulk_create.bulk_load_fanout import FANOUT

from test_helpers.terraform import read_terraform_output

EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()


@dataclass
class EtlConfig:
    bucket: str
    initial_trigger_key: str
    queue_history_key_prefix: str
    state_machine_history_key_prefix: str
    table_name: str


def get_etl_config(input_filename: str) -> EtlConfig:
    bulk_trigger_prefix = read_terraform_output("sds_etl.value.bulk_trigger_prefix")
    return EtlConfig(
        bucket=read_terraform_output("sds_etl.value.bucket"),
        initial_trigger_key=f"{bulk_trigger_prefix}/{input_filename}",
        queue_history_key_prefix=f"{ETL_QUEUE_HISTORY}/",
        state_machine_history_key_prefix=f"{ETL_STATE_MACHINE_HISTORY}/",
        table_name=read_terraform_output("dynamodb_table_name.value"),
    )


def _delete_objects_by_prefix(s3_client: S3Client, bucket: str, key_prefix: str):
    response = s3_client.list_objects(Bucket=bucket, Prefix=key_prefix)
    for item in response.get("Contents", []):
        s3_client.delete_object(Bucket=bucket, Key=item["Key"])


def clear_etl_state(s3_client: S3Client, etl_config: EtlConfig):

    s3_client.put_object(
        Bucket=etl_config.bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA
    )
    s3_client.put_object(
        Bucket=etl_config.bucket,
        Key=WorkerKey.TRANSFORM,
        Body=pkl_dumps_lz4(EMPTY_JSON_DATA),
    )
    s3_client.put_object(
        Bucket=etl_config.bucket,
        Key=WorkerKey.LOAD,
        Body=pkl_dumps_lz4(EMPTY_JSON_DATA),
    )
    for i in range(FANOUT):
        s3_client.put_object(
            Bucket=etl_config.bucket,
            Key=f"{WorkerKey.LOAD}.{i}",
            Body=pkl_dumps_lz4(EMPTY_JSON_DATA),
        )
    s3_client.delete_object(
        Bucket=etl_config.bucket, Key=etl_config.initial_trigger_key
    )

    _delete_objects_by_prefix(
        s3_client=s3_client,
        bucket=etl_config.bucket,
        key_prefix=etl_config.queue_history_key_prefix,
    )

    _delete_objects_by_prefix(
        s3_client=s3_client,
        bucket=etl_config.bucket,
        key_prefix=etl_config.state_machine_history_key_prefix,
    )
