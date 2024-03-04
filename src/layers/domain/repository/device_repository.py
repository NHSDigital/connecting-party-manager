from dataclasses import asdict
from typing import TYPE_CHECKING

from domain.core.device import (
    Device,
    DeviceCreatedEvent,
    DeviceKey,
    DeviceKeyAddedEvent,
    DeviceType,
)

from .errors import ItemNotFound
from .keys import TableKeys, strip_key_prefix
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository
from .transaction import ConditionExpression, TransactionItem, TransactionStatement

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import QueryOutputTypeDef


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def handle_DeviceCreatedEvent(
        self, event: DeviceCreatedEvent, entity: Device
    ) -> TransactionItem:
        pk = TableKeys.DEVICE.key(event.id)
        pk_1 = TableKeys.DEVICE_TYPE.key(event.type)
        return TransactionItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=pk, pk_1=pk_1, sk_1=pk, **asdict(event)),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def handle_DeviceKeyAddedEvent(self, event: DeviceKeyAddedEvent, entity: Device):
        pk = TableKeys.DEVICE.key(event.id)
        sk = TableKeys.DEVICE_KEY.key(event.key)
        pk_2 = TableKeys.DEVICE_KEY_TYPE.key(event.type)
        return TransactionItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=pk, sk=sk, pk_1=sk, sk_1=sk, pk_2=pk_2, sk_2=sk, **asdict(event)
                ),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def query_by_key_type(self, key_type, **kwargs) -> "QueryOutputTypeDef":
        pk_2 = TableKeys.DEVICE_KEY_TYPE.key(key_type)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_2",
            "KeyConditionExpression": "pk_2 = :pk_2",
            "ExpressionAttributeValues": {":pk_2": marshall_value(pk_2)},
        }
        return self.client.query(**args, **kwargs)

    def query_by_device_type(self, type: DeviceType, **kwargs) -> "QueryOutputTypeDef":
        pk_1 = TableKeys.DEVICE_TYPE.key(type)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1",
            "ExpressionAttributeValues": {
                ":pk_1": marshall_value(pk_1),
            },
        }
        return self.client.query(**args, **kwargs)

    def read_by_key(self, key) -> Device:
        pk_1 = TableKeys.DEVICE_KEY.key(key)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1 AND sk_1 = :pk_1",
            "ExpressionAttributeValues": {":pk_1": marshall_value(pk_1)},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(key)
        (item,) = items
        return self.read(strip_key_prefix(item["pk"]))

    def read(self, id) -> Device:
        pk = TableKeys.DEVICE.key(id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": marshall_value(pk)},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(id)

        keys = TableKeys.DEVICE_KEY.filter_and_group(items, key="sk")
        # pages = TableKeys.DEVICE_PAGE.filter_and_group(items, key="sk")
        # relationships = TableKeys.DEVICE_RELATIONSHIP.filter_and_group(items, key="sk")
        (device,) = TableKeys.DEVICE.filter(items, key="sk")

        return Device(
            keys={id_: DeviceKey(**data) for id_, data in keys},
            # pages={id_: DevicePage(values=data) for id_, data in pages},
            # relationships={id_: Relationship(**data) for id_, data in relationships},
            **device,
        )

    # def handle_DeviceKeyRemovedEvent(
    #     self, event: DeviceKeyRemovedEvent, entity: Device
    # ):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_KEY.key(event.key)
    #     return {
    #         "Delete": {
    #             "TableName": self.table_name,
    #             "Key": marshall(pk=pk, sk=sk),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }

    # def handle_DeviceUpdatedEvent(self, event: DeviceUpdatedEvent, entity: Device):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     return {
    #         "Put": {
    #             "TableName": self.table_name,
    #             "Item": marshall(pk=pk, sk=pk, **asdict(event)),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }

    # def handle_DeviceDeletedEvent(self, event: DeviceDeletedEvent, entity: Device):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     return {
    #         "Delete": {
    #             "TableName": self.table_name,
    #             "Key": marshall(pk=pk, sk=pk),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }

    # def handle_RelationshipAddedEvent(
    #     self, event: RelationshipAddedEvent, entity: Device
    # ):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_RELATIONSHIP.key(event.target)
    #     return {
    #         "Put": {
    #             "TableName": self.table_name,
    #             "Item": marshall(
    #                 pk=pk, sk=sk, **asdict(event)
    #             ),
    #             "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
    #         }
    #     }

    # def handle_RelationshipRemovedEvent(
    #     self, event: RelationshipRemovedEvent, entity: Device
    # ):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_RELATIONSHIP.key(event.target)
    #     return {
    #         "Delete": {
    #             "TableName": self.table_name,
    #             "Key": marshall(pk=pk, sk=sk),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }

    # def handle_DevicePageAddedEvent(self, event: DevicePageAddedEvent, entity: Device):
    #     page = entity.get_page(event.page)
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_PAGE.key(event.page)

    #     return {
    #         "Put": {
    #             "TableName": self.table_name,
    #             "Item": marshall(
    #                 pk=pk, sk=sk, pk_1=pk, sk_1=sk, **page.values
    #             ),
    #             "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
    #         }
    #     }

    # def handle_DevicePageRemovedEvent(
    #     self, event: DevicePageRemovedEvent, entity: Device
    # ):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_PAGE.key(event.page)
    #     return {
    #         "Delete": {
    #             "TableName": self.table_name,
    #             "Key": marshall(pk=pk, sk=sk),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }

    # def handle_DevicePageUpdatedEvent(
    #     self, event: DevicePageUpdatedEvent, entity: Device
    # ):
    #     page = entity.get_page(event.page)
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_PAGE.key(event.page)
    #     return {
    #         "Put": {
    #             "TableName": self.table_name,
    #             "Item": marshall(
    #                 pk=pk, sk=sk, pk_1=pk, sk_1=sk, **page.values
    #             ),
    #             "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
    #         }
    #     }
