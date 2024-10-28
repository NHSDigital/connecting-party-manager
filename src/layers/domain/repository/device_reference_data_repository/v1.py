from enum import StrEnum

from attr import asdict
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.repository.device_repository.v2 import create_device_index
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import TransactItem, update_transactions


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
        )

    def handle_DeviceReferenceDataCreatedEvent(
        self, event: DeviceReferenceDataCreatedEvent
    ) -> TransactItem:
        data = asdict(event)
        data["pk_1"] = TableKey.PRODUCT_TEAM_KEY.key(
            event.product_team_id, TableKey.PRODUCT_TEAM, event.product_id
        )
        data["sk_1"] = TableKey.DEVICE_REFERENCE_DATA.key(event.id)
        return create_device_reference_data(
            table_name=self.table_name, id=event.id, data=data, root=True
        )

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ) -> TransactItem:
        pk = TableKey.DEVICE_REFERENCE_DATA.key(event.id)
        data = asdict(event)
        data.pop("id")
        return update_transactions(
            table_name=self.table_name, primary_keys=[marshall(pk=pk, sk=pk)], data=data
        )

    def _query(
        self,
        product_team_id: str,
        product_id: str,
        device_reference_data_id: str,
        sk_query_type: QueryType,
    ) -> list[dict]:
        pk_1 = TableKey.PRODUCT_TEAM_KEY.key(
            product_team_id, TableKey.PRODUCT_TEAM, product_id
        )
        sk_1 = TableKey.DEVICE_REFERENCE_DATA.key(device_reference_data_id)
        sk_condition = sk_query_type.format("sk_1", ":sk_1")
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": f"pk_1 = :pk_1 AND {sk_condition}",
            "ExpressionAttributeValues": marshall(**{":pk_1": pk_1, ":sk_1": sk_1}),
        }
        result = self.client.query(**args)
        return result["Items"]

    def read(
        self, product_team_id: str, product_id: str, device_reference_data_id: str
    ) -> DeviceReferenceData:
        items = self._query(
            product_team_id=product_team_id,
            product_id=product_id,
            device_reference_data_id=device_reference_data_id,
            sk_query_type=QueryType.EQUALS,
        )
        try:
            (item,) = items
        except ValueError:
            raise ItemNotFound(
                product_team_id,
                product_id,
                device_reference_data_id,
                item_type=DeviceReferenceData,
            )
        return DeviceReferenceData(**unmarshall(item))

    def search(self, product_team_id: str, product_id: str):
        items = self._query(
            product_team_id=product_team_id,
            product_id=product_id,
            device_reference_data_id="",
            sk_query_type=QueryType.BEGINS_WITH,
        )
        return [DeviceReferenceData(**unmarshall(item)) for item in items]
