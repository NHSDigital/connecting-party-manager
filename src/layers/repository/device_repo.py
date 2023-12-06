from domain.core.device import (
    Device,
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceKey,
    DeviceKeyAddedEvent,
    DeviceKeyRemovedEvent,
    DevicePage,
    DevicePageAddedEvent,
    DevicePageRemovedEvent,
    DevicePageUpdatedEvent,
    DeviceUpdatedEvent,
    Relationship,
    RelationshipAddedEvent,
    RelationshipRemovedEvent,
)
from repository.keys import (
    device_key_sk,
    device_page_sk,
    device_pk,
    device_relationship_sk,
    ods_pk,
)

from .errors import NotFoundException
from .repository import Repository
from .utils import marshall, unmarshall


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def handle_DeviceCreatedEvent(self, event: DeviceCreatedEvent, entity: Device):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_pk(event.id),
                        "pk_1": ods_pk(event.ods_code),
                        "sk_1": device_pk(event.id),
                        "name": event.name,
                        "type": event.type,
                        "ods_code": event.ods_code,
                        "product_team_id": event.product_team_id,
                        "status": event.status,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_DeviceUpdatedEvent(self, event: DeviceUpdatedEvent, entity: Device):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_pk(event.id),
                        "name": event.name,
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_DeviceDeletedEvent(self, event: DeviceDeletedEvent, entity: Device):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_pk(event.id),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_RelationshipAddedEvent(
        self, event: RelationshipAddedEvent, entity: Device
    ):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_relationship_sk(event.target),
                        "pk_1": device_relationship_sk(event.target),
                        "sk_1": device_pk(event.id),
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_RelationshipRemovedEvent(
        self, event: RelationshipRemovedEvent, entity: Device
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_relationship_sk(event.target),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_DeviceKeyAddedEvent(self, event: DeviceKeyAddedEvent, entity: Device):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_key_sk(event.key),
                        "pk_1": device_key_sk(event.key),
                        "sk_1": device_key_sk(event.key),
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_DeviceKeyRemovedEvent(
        self, event: DeviceKeyRemovedEvent, entity: Device
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_key_sk(event.key),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_DevicePageAddedEvent(self, event: DevicePageAddedEvent, entity: Device):
        page = entity.get_page(event.page)
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_page_sk(event.page),
                        "pk_1": device_pk(event.id),
                        "sk_1": device_page_sk(event.page),
                        **page.values,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_DevicePageRemovedEvent(
        self, event: DevicePageRemovedEvent, entity: Device
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_page_sk(event.page),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_DevicePageUpdatedEvent(
        self, event: DevicePageUpdatedEvent, entity: Device
    ):
        page = entity.get_page(event.page)
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": device_pk(event.id),
                        "sk": device_page_sk(event.page),
                        "pk_1": device_pk(event.id),
                        "sk_1": device_page_sk(event.page),
                        **page.values,
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def read_by_key(self, key) -> Device:
        pk_1 = device_key_sk(key)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1 AND sk_1 = :pk_1",
            "ExpressionAttributeValues": {":pk_1": {"S": pk_1}},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise NotFoundException()

        (item,) = items

        return self.read(item["pk"].split("#", 1)[1])

    def read(self, id) -> Device:
        pk = device_pk(id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": {"S": pk}},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]

        pages = [v for v in items if v["sk"].startswith("DP#")]
        keys = [v for v in items if v["sk"].startswith("DK#")]
        relationships = [v for v in items if v["sk"].startswith("DR#")]
        device = [v for v in items if v["sk"].startswith("D#")][0]

        def extract_sk(record):
            return record["sk"].split("#", 1)[1]

        def remove_keys(pk=None, sk=None, pk_1=None, sk_1=None, **values):  # NOSONAR
            return values

        return Device(
            id=id,
            relationships={
                extract_sk(r): Relationship(**remove_keys(**r)) for r in relationships
            },
            keys={extract_sk(k): DeviceKey(**remove_keys(**k)) for k in keys},
            pages={extract_sk(p): DevicePage(values=remove_keys(**p)) for p in pages},
            **device,
        )
