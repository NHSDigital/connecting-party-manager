"""
Generate the lambda global variables (i.e. cache) for
both the load_bulk and load_update workers
"""

import boto3
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from sds.epr.bulk_create.bulk_repository import BulkRepository


class LoadWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str
    TABLE_NAME: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


class LoadWorkerCache:
    def __init__(self):
        self.S3_CLIENT = boto3.client("s3")
        self.ENVIRONMENT = LoadWorkerEnvironment.build()
        self.REPOSITORY = BulkRepository(
            table_name=self.ENVIRONMENT.TABLE_NAME, dynamodb_client=dynamodb_client()
        )
        self.MAX_RECORDS = 150_000
