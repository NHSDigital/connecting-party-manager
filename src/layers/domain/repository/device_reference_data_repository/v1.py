from attr import asdict
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
)
from domain.repository.device_repository.v2 import create_device_index
from domain.repository.keys.v3 import TableKey
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
