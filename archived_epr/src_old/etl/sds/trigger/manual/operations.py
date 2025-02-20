from typing import TYPE_CHECKING

from etl_utils.constants import ETL_STATE_MACHINE_HISTORY

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class ExecutionHistoryEmpty(Exception):
    def __init__(self, bucket, key):
        super().__init__(self, f"s3://{bucket}/{key} is empty")


def validate_bucket_contents(s3_client: "S3Client", etl_bucket: str):
    response = s3_client.list_objects_v2(
        Bucket=etl_bucket, Prefix=f"{ETL_STATE_MACHINE_HISTORY}/"
    )
    if "Contents" not in response:
        raise ExecutionHistoryEmpty(
            bucket=etl_bucket, key=f"{ETL_STATE_MACHINE_HISTORY}/"
        )

    return response
