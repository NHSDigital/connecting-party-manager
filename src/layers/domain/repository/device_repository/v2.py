# from collections import defaultdict
from functools import partial

from attr import asdict as _asdict
from domain.core.device.v2 import (
    Device,
    DeviceCreatedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceUpdatedEvent,
)
from domain.core.device_key.v2 import DeviceKey
from domain.repository.errors import ItemNotFound
from domain.repository.keys import TableKeys
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)


def asdict(obj) -> dict:
    return _asdict(obj, recurse=False)


def _dynamodb_update_expression(updated_fields: dict):
    expression_attribute_names = {}
    expression_attribute_values = {}
    update_clauses = []

    for field_name, value in updated_fields.items():
        field_name_placeholder = f"#{field_name}"
        field_value_placeholder = f":{field_name}"

        update_clauses.append(f"{field_name_placeholder} = {field_value_placeholder}")
        expression_attribute_names[field_name_placeholder] = field_name
        expression_attribute_values[field_value_placeholder] = marshall_value(value)

    update_expression = "SET " + ", ".join(update_clauses)

    return dict(
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )


def _device_primary_keys(device_id: str, device_keys: list[DeviceKey]) -> list[dict]:
    """
    Generates all the fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary keys (i.e. pk + sk) for the provided Device. This is one primary key
    plus an additional primary key for every value of Device.keys
    """
    root_primary_key = marshall(
        pk=TableKeys.DEVICE.key(device_id), sk=TableKeys.DEVICE.key(device_id)
    )
    non_root_primary_keys = [
        marshall(pk=pk, sk=pk)
        for pk in (TableKeys.DEVICE.key(k.key_type, k.key_value) for k in device_keys)
    ]
    return [root_primary_key] + non_root_primary_keys


def handle_update_device(
    table_name: str, id: str, keys: list[DeviceKey], data: dict
) -> list[TransactItem]:
    primary_keys = _device_primary_keys(device_id=id, device_keys=keys)
    update_expression = _dynamodb_update_expression(updated_fields=data)
    update_statement = partial(
        TransactionStatement,
        TableName=table_name,
        ConditionExpression=ConditionExpression.MUST_EXIST,
        **update_expression,
    )
    transact_items = [
        TransactItem(Update=update_statement(Key=key)) for key in primary_keys
    ]
    return transact_items


def handle_create_device(
    table_name: str, key_parts: tuple[str], device_data: dict
) -> TransactItem:
    key = TableKeys.DEVICE.key(*key_parts)
    return TransactItem(
        Put=TransactionStatement(
            TableName=table_name,
            Item=marshall(pk=key, sk=key, root=True, **device_data),
            ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
        )
    )


def handle_delete_device(table_name: str, key_parts: tuple[str]) -> TransactItem:
    key = TableKeys.DEVICE.key(*key_parts)
    return TransactItem(
        Delete=TransactionStatement(
            TableName=table_name,
            Key=marshall(pk=key, sk=key),
            ConditionExpression=ConditionExpression.MUST_EXIST,
        )
    )


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def handle_DeviceCreatedEvent(self, event: DeviceCreatedEvent) -> TransactItem:
        return handle_create_device(
            table_name=self.table_name,
            key_parts=(event.id,),
            device_data=asdict(event),
        )

    def handle_DeviceUpdatedEvent(
        self, event: DeviceUpdatedEvent
    ) -> list[TransactItem]:
        keys = {DeviceKey(**key) for key in event.keys}
        return handle_update_device(
            table_name=self.table_name,
            id=event.id,
            keys=keys,
            data=asdict(event),
        )

    def handle_DeviceKeyAddedEvent(
        self, event: DeviceKeyAddedEvent
    ) -> list[TransactItem]:
        # Create a copy of the Device indexed against the new key
        device_data = asdict(event)
        device_data.pop("new_key")
        create_transaction = handle_create_device(
            table_name=self.table_name,
            key_parts=event.new_key.parts,
            device_data=device_data,
        )
        # Update the value of "keys" on all other copies of this Device
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.new_key}
        update_transactions = handle_update_device(
            table_name=self.table_name,
            id=event.id,
            keys=device_keys_before_update,
            data={"keys": event.keys},
        )
        return [create_transaction] + update_transactions

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> list[TransactItem]:
        # Delete the copy of the Device indexed against the deleted key
        delete_transaction = handle_delete_device(
            table_name=self.table_name, key_parts=event.deleted_key.parts
        )
        # Update the value of "keys" on all other copies of this Device
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.deleted_key}
        update_transactions = handle_update_device(
            table_name=self.table_name,
            id=event.id,
            keys=device_keys_before_update,
            data={"keys": event.keys},
        )
        return [delete_transaction] + update_transactions

    def read(self, *key_parts: str) -> Device:
        """
        Read the device by either id or key. If calling by id, then do:

            repository.read("123")

        If calling by key then you must include the key type (e.g. 'product_id'):

            repository.read("product_id", "123")

        """
        key = TableKeys.DEVICE.key(*key_parts)
        result = self.client.get_item(
            TableName=self.table_name, Key=marshall(pk=key, sk=key)
        )
        try:
            item = result["Item"]
        except KeyError:
            raise ItemNotFound(key_parts)
        return Device(**unmarshall(item))
