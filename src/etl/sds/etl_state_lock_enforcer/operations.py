from typing import TYPE_CHECKING

from etl_utils.constants import ETL_STATE_LOCK
from etl_utils.trigger.operations import object_exists

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def etl_state_lock_doesnt_exist_in_s3(s3_client: "S3Client", bucket: str):
    return not object_exists(s3_client=s3_client, bucket=bucket, key=ETL_STATE_LOCK)
