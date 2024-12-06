from typing import TYPE_CHECKING

from domain.core.device.v1 import Device


if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient


class EtlDeviceRepository:
    def __init__(self, table_name, dynamodb_client):
        self.table_name = table_name
        self.client: "DynamoDBClient" = dynamodb_client

    def read_if_exists(self, id: str) -> Device | None: ...
