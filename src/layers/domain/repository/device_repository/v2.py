from copy import copy
from functools import partial

from attr import asdict
from domain.core.compression import pkl_dumps_gzip, pkl_loads_gzip
from domain.core.device.v2 import (
    Device,
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceTag,
    DeviceTagAddedEvent,
    DeviceTagsAddedEvent,
    DeviceTagsClearedEvent,
    DeviceUpdatedEvent,
)
from domain.core.device_key.v2 import DeviceKey
from domain.core.enum import Status
from domain.core.event import Event
from domain.core.questionnaire.v2 import QuestionnaireResponseUpdatedEvent
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v2 import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v1 import batched
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)

ROOT_FIELDS_TO_COMPRESS = ["tags"]
NON_ROOT_FIELDS_TO_COMPRESS = ["questionnaire_responses"]
BATCH_GET_SIZE = 100


class TooManyResults(Exception):
    pass


def compress_device_fields(data: Event | dict, fields_to_compress=None) -> dict:
    _data = copy(data) if isinstance(data, dict) else asdict(data, recurse=False)

    # pop unknown keys
    unknown_keys = _data.keys() - set(Device.__fields__)
    for k in unknown_keys:
        _data.pop(k)

    # compress specified keys if they exist in the data
    fields_to_compress = (fields_to_compress or []) + ROOT_FIELDS_TO_COMPRESS
    fields_to_compress_that_exist = [f for f in fields_to_compress if f in _data]
    for field in fields_to_compress_that_exist:
        _data[field] = pkl_dumps_gzip(_data[field])
    return _data


def decompress_device_fields(device: dict):
    for field in ROOT_FIELDS_TO_COMPRESS:
        device[field] = pkl_loads_gzip(device[field])

    if device["root"] is False:
        for field in NON_ROOT_FIELDS_TO_COMPRESS:
            device[field] = pkl_loads_gzip(device[field])
    return device


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


def _device_root_primary_key(device_id: str) -> dict:
    """
    Generates one fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary key (i.e. pk + sk) for the provided Device, indexed by the Device ID
    """
    root_pk = TableKey.DEVICE.key(device_id)
    return marshall(pk=root_pk, sk=root_pk)


def _device_non_root_primary_keys(
    device_id: str, device_keys: list[DeviceKey], device_tags: list[DeviceTag]
) -> list[dict]:
    """
    Generates all the fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary keys (i.e. pk + sk) for the provided Device. This is one primary key
    for every value of Device.keys and Device.tags
    """
    root_pk = TableKey.DEVICE.key(device_id)
    device_key_primary_keys = [
        marshall(pk=pk, sk=pk)
        for pk in (TableKey.DEVICE.key(k.key_type, k.key_value) for k in device_keys)
    ]
    device_tag_primary_keys = [
        marshall(pk=pk, sk=root_pk)
        for pk in (TableKey.DEVICE_TAG.key(t.value) for t in device_tags)
    ]
    return device_key_primary_keys + device_tag_primary_keys


def _update_device_indexes(
    table_name: str, primary_keys: list[dict], data: dict
) -> list[TransactItem]:
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


def update_device_indexes(
    table_name: str,
    data: dict | DeviceUpdatedEvent,
    id: str,
    keys: list[DeviceKey],
    tags: list[DeviceTag],
):
    # Update the root device without compressing the 'questionnaire_responses' field
    root_primary_key = _device_root_primary_key(device_id=id)
    update_root_device_transactions = _update_device_indexes(
        table_name=table_name,
        primary_keys=[root_primary_key],
        data=compress_device_fields(data),
    )
    # Update non-root devices with compressed 'questionnaire_responses' field
    non_root_primary_keys = _device_non_root_primary_keys(
        device_id=id, device_keys=keys, device_tags=tags
    )
    update_non_root_devices_transactions = _update_device_indexes(
        table_name=table_name,
        primary_keys=non_root_primary_keys,
        data=compress_device_fields(
            data, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        ),
    )
    return update_root_device_transactions + update_non_root_devices_transactions


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


def create_device_index_batch(
    pk_key_parts: tuple[str],
    device_data: dict,
    sk_key_parts=None,
    pk_table_key: TableKey = TableKey.DEVICE,
    sk_table_key: TableKey = TableKey.DEVICE,
    root=False,
) -> TransactItem:
    pk = pk_table_key.key(*pk_key_parts)
    sk = sk_table_key.key(*sk_key_parts) if sk_key_parts else pk
    return {
        "PutRequest": {
            "Item": marshall(pk=pk, sk=sk, root=root, **device_data),
        },
    }


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
            device_data=compress_device_fields(event),
            root=True,
        )

    def handle_DeviceUpdatedEvent(
        self, event: DeviceUpdatedEvent
    ) -> list[TransactItem]:
        keys = {DeviceKey(**key) for key in event.keys}
        tags = {DeviceTag(__root__=tag) for tag in event.tags}
        return update_device_indexes(
            table_name=self.table_name, data=event, id=event.id, keys=keys, tags=tags
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
        inactive_data = compress_device_fields(event)
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
                pk_key_parts=(event.status, event.id),
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
                    pk_key_parts=(event.status, event.id),
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
        create_transaction = create_device_index(
            table_name=self.table_name,
            pk_key_parts=event.new_key.parts,
            device_data=compress_device_fields(
                event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
            ),
        )
        # Update the value of "keys" on all other copies of this Device
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
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
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
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
        create_transaction = create_device_index(
            table_name=self.table_name,
            pk_key_parts=(event.new_tag.value,),
            sk_key_parts=(event.id,),
            pk_table_key=TableKey.DEVICE_TAG,
            device_data={},
        )
        # Update the value of "tags" on all other copies of this Device
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
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

    def handle_DeviceTagsAddedEvent(self, event: DeviceTagsAddedEvent):
        # Create a copy of the Device indexed against the new tag
        device_data = compress_device_fields(
            event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )
        create_transactions = [
            create_device_index(
                table_name=self.table_name,
                pk_key_parts=(new_tag.value,),
                sk_key_parts=(event.id,),
                pk_table_key=TableKey.DEVICE_TAG,
                device_data=device_data,
            )
            for new_tag in event.new_tags
        ]

        # Update the value of "tags" on all other copies of this Device
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
        device_tags_before_update = device_tags - event.new_tags
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
        return create_transactions + update_transactions

    def handle_DeviceTagsClearedEvent(self, event: DeviceTagsClearedEvent):
        delete_tags_transactions = [
            delete_device_index(
                table_name=self.table_name,
                pk_key_parts=(tag.value,),
                sk_key_parts=(event.id,),
                pk_table_key=TableKey.DEVICE_TAG,
            )
            for tag in event.deleted_tags
        ]

        keys = {DeviceKey(**key) for key in event.keys}
        update_transactions = update_device_indexes(
            table_name=self.table_name,
            id=event.id,
            keys=keys,
            tags=[],
            data={"tags": []},
        )
        return delete_tags_transactions + update_transactions

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ):
        keys = {DeviceKey(**key) for key in event.entity_keys}
        tags = {DeviceTag(__root__=tag) for tag in event.entity_tags}
        return update_device_indexes(
            table_name=self.table_name,
            id=event.entity_id,
            keys=keys,
            tags=tags,
            data={
                "questionnaire_responses": event.questionnaire_responses,
                "updated_on": event.updated_on,
            },
        )

    def handle_bulk(self, item: dict) -> list[TransactItem]:
        create_device_transaction = create_device_index_batch(
            pk_key_parts=(item["id"],),
            device_data=compress_device_fields(item),
            root=True,
        )

        device_data = compress_device_fields(
            item, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )
        create_keys_transactions = [
            create_device_index_batch(
                pk_key_parts=(key["key_type"], key["key_value"]),
                device_data=device_data,
            )
            for key in item["keys"]
        ]
        create_tags_transactions = [
            create_device_index_batch(
                pk_key_parts=(DeviceTag(__root__=tag).value,),
                sk_key_parts=(item["id"],),
                pk_table_key=TableKey.DEVICE_TAG,
                device_data={},
            )
            for tag in item["tags"]
        ]
        return (
            [create_device_transaction]
            + create_keys_transactions
            + create_tags_transactions
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

        _device = unmarshall(item)
        return Device(**decompress_device_fields(_device))

    def read_inactive(self, *key_parts: str) -> Device:
        """
        Read the inactive device by id::

            repository.read("123")

        """
        pk = TableKey.DEVICE_STATUS.key(Status.INACTIVE, *key_parts)
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
        tag_value = DeviceTag(**kwargs).value
        pk = TableKey.DEVICE_TAG.key(tag_value)

        # Initial query to retrieve a list of all the root-device pk's
        response = self.client.query(
            ExpressionAttributeValues={":pk": marshall_value(pk)},
            KeyConditionExpression="pk = :pk",
            TableName=self.table_name,
        )
        # Not yet implemented: pagination
        if "LastEvaluatedKey" in response:
            raise TooManyResults(f"Too many results for query '{kwargs}'")

        device_keys = [
            {"pk": item["sk"], "sk": item["sk"]} for item in response.get("Items")
        ]

        # Retrieve all devices in batches until done
        db_devices = []
        for device_key_chunk in batched(device_keys, BATCH_GET_SIZE):
            while device_key_chunk:
                response = self.client.batch_get_item(
                    RequestItems={self.table_name: {"Keys": device_key_chunk}}
                )
                db_devices += response["Responses"].get(self.table_name)
                device_key_chunk = response["UnprocessedKeys"]

        # Convert to Device, sorted by 'pk', which would have been
        # the expected behaviour if tags in the database were
        # Device duplicates rather than references
        compressed_devices = map(unmarshall, db_devices)
        devices_as_dict = map(decompress_device_fields, compressed_devices)
        return [Device(**d) for d in sorted(devices_as_dict, key=lambda d: d["id"])]
