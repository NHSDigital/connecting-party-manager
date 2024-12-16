from typing import TYPE_CHECKING

from domain.core.device.v1 import Device
from domain.repository.device_repository.v1 import decompress_device_fields
from domain.repository.keys.v1 import TableKey
from domain.repository.marshall import marshall, unmarshall

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient


class EtlDeviceRepository:
    def __init__(self, table_name, dynamodb_client):
        self.table_name = table_name
        self.client: "DynamoDBClient" = dynamodb_client

    def read_if_exists(self, id: str) -> Device | None:
        """
        Read Device directly by pk - intended for use
        reading by key with unique_identifier
        (asid or cpa_id) in the ETL
        """
        pk = TableKey.DEVICE.key(id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": f"pk = :pk",
            "ExpressionAttributeValues": marshall(**{":pk": pk}),
        }
        result = self.client.query(**args)
        try:
            (item,) = map(unmarshall, result["Items"])
        except ValueError:
            return None
        return Device(**decompress_device_fields(item))
