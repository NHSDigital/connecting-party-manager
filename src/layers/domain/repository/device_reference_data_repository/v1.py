from enum import StrEnum

from attr import asdict
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.repository.device_repository.v2 import create_device_index
from domain.repository.keys.v3 import TableKey
from domain.repository.repository.v3 import Repository
from domain.repository.transaction import TransactItem


class QueryType(StrEnum):
    EQUALS = "{} = {}"
    BEGINS_WITH = "begins_with({}, {})"


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
            table_key=TableKey.DEVICE_REFERENCE_DATA,
            parent_table_keys=(TableKey.PRODUCT_TEAM, TableKey.CPM_PRODUCT),
        )

    def read(self, product_team_id: str, product_id: str, id: str):
        return super()._read(parent_ids=(product_team_id, product_id), id=id)

    def search(self, product_team_id: str, product_id: str):
        return super()._query(parent_ids=(product_team_id, product_id))

    def handle_DeviceReferenceDataCreatedEvent(
        self, event: DeviceReferenceDataCreatedEvent
    ) -> TransactItem:
        return self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id, event.product_id),
            data=asdict(event),
            root=True,
        )

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ) -> TransactItem:
        data = asdict(event)
        data.pop("id")
        return self.update_indexes(id=event.id, keys=[], data=data)
