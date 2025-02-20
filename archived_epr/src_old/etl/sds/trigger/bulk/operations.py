from typing import TYPE_CHECKING

from etl_utils.constants import CHANGELOG_NUMBER
from etl_utils.trigger.operations import object_exists

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_s3 import S3Client


class TableNotEmpty(Exception):
    def __init__(self, table_name: str):
        super().__init__(self, f"Expected empty table '{table_name}'")


class ChangelogNumberExists(Exception):
    def __init__(self, bucket, key):
        super().__init__(
            self, f"s3://{bucket}/{key} should not exist when using bulk trigger"
        )


def validate_no_changelog_number(s3_client: "S3Client", source_bucket):
    if object_exists(s3_client=s3_client, bucket=source_bucket, key=CHANGELOG_NUMBER):
        raise ChangelogNumberExists(bucket=source_bucket, key=CHANGELOG_NUMBER)


def validate_database_is_empty(dynamodb_client: "DynamoDBClient", table_name: str):
    response = dynamodb_client.scan(TableName=table_name, Limit=1, Select="COUNT")
    if response["Count"] > 0:
        raise TableNotEmpty(table_name=table_name)
