from functools import partial

from attr import asdict as _asdict
from domain.core.device.v2 import (
    Device,
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceTag,
    DeviceTagAddedEvent,
    DeviceUpdatedEvent,
)
from domain.core.device_key.v2 import DeviceKey
from domain.core.questionnaire.v2 import QuestionnaireResponseUpdatedEvent
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v2 import TableKey
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


def _device_primary_keys(
    device_id: str, device_keys: list[DeviceKey], device_tags: list[DeviceTag]
) -> list[dict]:
    """
    Generates all the fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary keys (i.e. pk + sk) for the provided Device. This is one primary key
    plus an additional primary key for every value of Device.keys
    """
    root_pk = TableKey.DEVICE.key(device_id)
    root_primary_key = marshall(pk=root_pk, sk=root_pk)
    device_key_primary_keys = [
        marshall(pk=pk, sk=pk)
        for pk in (TableKey.DEVICE.key(k.key_type, k.key_value) for k in device_keys)
    ]
    device_tag_primary_keys = [
        marshall(pk=pk, sk=root_pk)
        for pk in (TableKey.DEVICE_TAG.key(t.value) for t in device_tags)
    ]
    return [root_primary_key] + device_key_primary_keys + device_tag_primary_keys


def update_device_indexes(
    table_name: str,
    id: str,
    keys: list[DeviceKey],
    data: dict,
    tags: list[DeviceTag] = None,
) -> list[TransactItem]:
    tags = [] if tags is None else tags

    primary_keys = _device_primary_keys(
        device_id=id, device_keys=keys, device_tags=tags
    )
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


def create_device_index(
    table_name: str,
    pk_key_parts: tuple[str],
    device_data: dict,
    sk_key_parts=None,
    pk_table_key: TableKey = TableKey.DEVICE,
    sk_table_key: TableKey = TableKey.DEVICE,
    root=False,
) -> TransactItem:
    pk = pk_table_key.key(*pk_key_parts)
    sk = sk_table_key.key(*sk_key_parts) if sk_key_parts else pk
    return TransactItem(
        Put=TransactionStatement(
            TableName=table_name,
            Item=marshall(pk=pk, sk=sk, root=root, **device_data),
            ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
        )
    )


def delete_device_index(
    table_name: str,
    pk_key_parts: tuple[str],
    sk_key_parts=None,
    pk_table_key: TableKey = TableKey.DEVICE,
    sk_table_key: TableKey = TableKey.DEVICE,
) -> TransactItem:
    pk = pk_table_key.key(*pk_key_parts)
    sk = sk_table_key.key(*sk_key_parts) if sk_key_parts else pk
    return TransactItem(
        Delete=TransactionStatement(
            TableName=table_name,
            Key=marshall(pk=pk, sk=sk),
            ConditionExpression=ConditionExpression.MUST_EXIST,
        )
    )


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def handle_DeviceCreatedEvent(self, event: DeviceCreatedEvent) -> TransactItem:
        return create_device_index(
            table_name=self.table_name,
            pk_key_parts=(event.id,),
            device_data=asdict(event),
            root=True,
        )

    def handle_DeviceUpdatedEvent(
        self, event: DeviceUpdatedEvent
    ) -> list[TransactItem]:
        keys = {DeviceKey(**key) for key in event.keys}
        tags = {DeviceTag(**tag) for tag in event.tags}
        return update_device_indexes(
            table_name=self.table_name,
            id=event.id,
            keys=keys,
            tags=tags,
            data=asdict(event),
        )

    def handle_DeviceDeletedEvent(
        self, event: DeviceDeletedEvent
    ) -> list[TransactItem]:
        # Inactive Devices have tags removed so that they are
        # no longer searchable
        delete_transactions = [
            delete_device_index(
                table_name=self.table_name,
                pk_key_parts=(DeviceTag(**tag).value,),
                sk_key_parts=(event.id,),
                pk_table_key=TableKey.DEVICE_TAG,
            )
            for tag in event.deleted_tags
        ]

        # Prepare data for the inactive copies
        inactive_data = asdict(event)
        inactive_data.pop("deleted_tags")
        inactive_data["status"] = "inactive"

        # Collect keys for the original devices
        original_keys = {DeviceKey(**key) for key in event.keys}

        # Create copy of original device and indexes with new pk and sk
        inactive_root_copy_transactions = []
        inactive_root_copy_transactions.append(
            create_device_index(
                table_name=self.table_name,
                pk_table_key=TableKey.DEVICE_STATUS,
                pk_key_parts=(event.status,),
                sk_key_parts=(event.id,),
                device_data=inactive_data,
                root=True,
            )
        )

        inactive_key_indexes_copy_transactions = []
        for key in original_keys:
            inactive_key_indexes_copy_transactions.append(
                create_device_index(
                    table_name=self.table_name,
                    pk_table_key=TableKey.DEVICE_STATUS,
                    pk_key_parts=(event.status,),
                    sk_key_parts=key.parts,
                    device_data=inactive_data,
                    root=False,
                )
            )

        # Create delete transactions for original device and key indexes
        original_root_delete_transactions = []
        original_root_delete_transactions.append(
            delete_device_index(
                table_name=self.table_name,
                pk_key_parts=(event.id,),
                pk_table_key=TableKey.DEVICE,
            )
        )

        original_key_indexes_delete_transactions = []
        for key in original_keys:
            original_key_indexes_delete_transactions.append(
                delete_device_index(
                    table_name=self.table_name,
                    pk_key_parts=key.parts,
                    pk_table_key=TableKey.DEVICE,
                )
            )

        return (
            delete_transactions
            + inactive_root_copy_transactions
            + inactive_key_indexes_copy_transactions
            + original_root_delete_transactions
            + original_key_indexes_delete_transactions
        )

    def handle_DeviceKeyAddedEvent(
        self, event: DeviceKeyAddedEvent
    ) -> list[TransactItem]:
        # Create a copy of the Device indexed against the new key
        device_data = asdict(event)
        device_data.pop("new_key")
        create_transaction = create_device_index(
            table_name=self.table_name,
            pk_key_parts=event.new_key.parts,
            device_data=device_data,
        )
        # Update the value of "keys" on all other copies of this Device
        device_tags = {DeviceTag(**tag) for tag in event.tags}
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.new_key}
        update_transactions = update_device_indexes(
            table_name=self.table_name,
            id=event.id,
            keys=device_keys_before_update,
            tags=device_tags,
            data={
                "keys": event.keys,
                "updated_on": event.updated_on,
            },
        )
        return [create_transaction] + update_transactions

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> list[TransactItem]:
        # Delete the copy of the Device indexed against the deleted key
        delete_transaction = delete_device_index(
            table_name=self.table_name, pk_key_parts=event.deleted_key.parts
        )
        # Update the value of "keys" on all other copies of this Device
        device_tags = {DeviceTag(**tag) for tag in event.tags}
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.deleted_key}
        update_transactions = update_device_indexes(
            table_name=self.table_name,
            id=event.id,
            keys=device_keys_before_update,
            tags=device_tags,
            data={
                "keys": event.keys,
                "updated_on": event.updated_on,
            },
        )
        return [delete_transaction] + update_transactions

    def handle_DeviceTagAddedEvent(
        self, event: DeviceTagAddedEvent
    ) -> list[TransactItem]:
        # Create a copy of the Device indexed against the new tag
        device_data = asdict(event)
        device_data.pop("new_tag")
        create_transaction = create_device_index(
            table_name=self.table_name,
            pk_key_parts=(event.new_tag.value,),
            sk_key_parts=(event.id,),
            pk_table_key=TableKey.DEVICE_TAG,
            device_data=device_data,
        )
        # Update the value of "tags" on all other copies of this Device
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_tags = {DeviceTag(**tag) for tag in event.tags}
        device_tags_before_update = device_tags - {event.new_tag}
        update_transactions = update_device_indexes(
            table_name=self.table_name,
            id=event.id,
            keys=device_keys,
            tags=device_tags_before_update,
            data={
                "tags": event.tags,
                "updated_on": event.updated_on,
            },
        )
        return [create_transaction] + update_transactions

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ):
        device_keys = {DeviceKey(**key) for key in event.entity_keys}
        device_tags = {DeviceTag(**tag) for tag in event.entity_tags}
        return update_device_indexes(
            table_name=self.table_name,
            id=event.entity_id,
            keys=device_keys,
            tags=device_tags,
            data={
                "questionnaire_responses": event.questionnaire_responses,
                "updated_on": event.updated_on,
            },
        )

    def read(self, *key_parts: str) -> Device:
        """
        Read the device by either id or key. If calling by id, then do:

            repository.read("123")

        If calling by key then you must include the key type (e.g. 'product_id'):

            repository.read("product_id", "123")

        """
        key = TableKey.DEVICE.key(*key_parts)
        result = self.client.get_item(
            TableName=self.table_name, Key=marshall(pk=key, sk=key)
        )
        try:
            item = result["Item"]
        except KeyError:
            raise ItemNotFound(key_parts)
        return Device(**unmarshall(item))

    def read_inactive(self, *key_parts: str) -> Device:
        """
        Read the inactive device by either id or key. If calling by id, then do:

            repository.read("123")

        If calling by key then you must include the key type (e.g. 'product_id'):

            repository.read("product_id", "123")

        """
        pk = "DS#inactive"
        sk = TableKey.DEVICE.key(*key_parts)

        result = self.client.get_item(
            TableName=self.table_name, Key=marshall(pk=pk, sk=sk)
        )
        try:
            item = result["Item"]
        except KeyError:
            raise ItemNotFound(key_parts)
        return Device(**unmarshall(item))

    def query_by_tag(self, **kwargs) -> list[Device]:
        """
        Query the device by predefined tags:

            repository.query_by_tag(foo="123", bar="456")
        """
        tag_components = list(map(tuple, kwargs.items()))
        tag_value = DeviceTag(components=tag_components).value
        pk = TableKey.DEVICE_TAG.key(tag_value)

        response = self.client.query(
            ExpressionAttributeValues={":pk": marshall_value(pk)},
            KeyConditionExpression="pk = :pk",
            TableName=self.table_name,
        )
        items = response["Items"]
        return [Device(**unmarshall(item)) for item in items]
