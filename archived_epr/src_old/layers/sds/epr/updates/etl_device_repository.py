from domain.core.device.v1 import Device
from domain.repository.device_repository.v1 import (
    decompress_device_fields,
    delete_tag_index,
)
from domain.repository.keys.v1 import TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.repository.v1 import Repository
from sds.epr.updates.etl_device import DeviceHardDeletedEvent


class EtlDeviceRepository(Repository):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=Device,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM, TableKey.CPM_PRODUCT),
            table_key=TableKey.DEVICE,
        )

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
        return self.model(**decompress_device_fields(item))

    def handle_DeviceHardDeletedEvent(self, event: DeviceHardDeletedEvent):
        delete_root_index = self.delete_index(event.id)
        delete_key_indexes = [self.delete_index(key["key_value"]) for key in event.keys]
        tag_delete_transactions = [
            delete_tag_index(
                table_name=self.table_name,
                device_id=event.id,
                tag_value=tag,
            )
            for tag in event.tags
        ]
        return [delete_root_index] + delete_key_indexes + tag_delete_transactions
