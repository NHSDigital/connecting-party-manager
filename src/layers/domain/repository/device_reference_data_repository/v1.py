from attr import asdict
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
)
from domain.repository.device_repository.v2 import create_device_index
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import TransactItem


def create_device_reference_data(table_name: str, id: str, data: dict, root: bool):
    return create_device_index(
        table_name=table_name,
        pk_key_parts=(id,),
        pk_table_key=TableKey.DEVICE_REFERENCE_DATA,
        sk_table_key=TableKey.DEVICE_REFERENCE_DATA,
        device_data=data,
        root=root,
    )


class DeviceReferenceDataRepository(Repository[DeviceReferenceData]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=DeviceReferenceData,
            dynamodb_client=dynamodb_client,
        )

    def handle_DeviceReferenceDataCreatedEvent(
        self, event: DeviceReferenceDataCreatedEvent
    ) -> TransactItem:
        return create_device_reference_data(
            table_name=self.table_name, id=event.id, data=asdict(event), root=True
        )

    def read(
        self, product_team_id: str, product_id: str, device_reference_data_id: str
    ) -> DeviceReferenceData:
        # TODO: in future switch the pk / sk to pk_read / sk_read on the GSI
        pk = TableKey.DEVICE_REFERENCE_DATA.key(device_reference_data_id)
        sk = TableKey.DEVICE_REFERENCE_DATA.key(device_reference_data_id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND sk = :sk",
            "ExpressionAttributeValues": marshall(**{":pk": pk, ":sk": sk}),
        }
        result = self.client.query(**args)

        try:
            (item,) = result["Items"]
        except ValueError:
            raise ItemNotFound(
                product_team_id,
                product_id,
                device_reference_data_id,
                item_type=DeviceReferenceData,
            )
        return DeviceReferenceData(**unmarshall(item))
