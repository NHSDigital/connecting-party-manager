from copy import copy
from functools import partial

from attr import asdict
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
from domain.repository.compression import pkl_dumps_gzip, pkl_loads_gzip
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v2 import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)

TAGS = "tags"
ROOT_FIELDS_TO_COMPRESS = [TAGS]
NON_ROOT_FIELDS_TO_COMPRESS = ["questionnaire_responses"]
BATCH_GET_SIZE = 100


class TooManyResults(Exception):
    pass


class CannotDropMandatoryFields(Exception):
    def __init__(self, bad_fields: set[str]) -> None:
        super().__init__(f"Cannot drop mandatory fields: {', '.join(bad_fields)}")


def compress_device_fields(data: Event | dict, fields_to_compress=None) -> dict:
    _data = copy(data) if isinstance(data, dict) else asdict(data, recurse=False)

    # Pop unknown keys
    unknown_keys = _data.keys() - set(Device.__fields__)
    for k in unknown_keys:
        _data.pop(k)

    # Compress specified keys if they exist in the data
    fields_to_compress = (fields_to_compress or []) + ROOT_FIELDS_TO_COMPRESS
    fields_to_compress_that_exist = [f for f in fields_to_compress if _data.get(f)]
    for field in fields_to_compress_that_exist:
        # Only proceed if the field is not empty
        if field == TAGS:
            # Tags are doubly compressed: first compress each tag in the list
            _data[field] = [pkl_dumps_gzip(tag) for tag in _data[field]]
        # Compress the entire field (which includes the doubly compressed tags)
        _data[field] = pkl_dumps_gzip(_data[field])
    return _data


def decompress_device_fields(device: dict):
    for field in ROOT_FIELDS_TO_COMPRESS:
        if device.get(field):  # Check if the field is present and not empty
            device[field] = pkl_loads_gzip(device[field])  # First decompression
            if field == TAGS:  # Tags are doubly compressed.
                # Second decompression: Decompress each tag in the list
                device[field] = [pkl_loads_gzip(tag) for tag in device[field]]

    # Decompress non-root fields if the device is not a root and fields exist
    if not device.get("root"):  # Use get to handle missing 'root' field
        for field in NON_ROOT_FIELDS_TO_COMPRESS:
            if device.get(field):  # Check if the field is present and non empty
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
) -> dict:
    """
    Difference between `create_device_index` and `create_device_index_batch`:

    `create_device_index` is intended for the event-based
    handlers (e.g. `handle_DeviceCreatedEvent`) which are called by the base
    `write` method, which expects `TransactItem`s for use with `client.transact_write_items`

    `create_device_index_batch` is intended the device-based handler
    `handle_bulk` which is called by the base method `write_bulk`, which expects
    `BatchWriteItem`s which we render as a `dict` for use with `client.batch_write_items`
    """
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
                pk_key_parts=(DeviceTag(__root__=tag).value,),
                sk_key_parts=(event.id,),
                pk_table_key=TableKey.DEVICE_TAG,
            )
            for tag in event.deleted_tags
        ]

        # Prepare data for the inactive copies
        inactive_data = compress_device_fields(event)
        inactive_data["status"] = str(Status.INACTIVE)

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
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.new_key}
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
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
        device_keys = {DeviceKey(**key) for key in event.keys}
        device_keys_before_update = device_keys - {event.deleted_key}
        device_tags = {DeviceTag(__root__=tag) for tag in event.tags}
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
            device_data=compress_device_fields(
                event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
            ),
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
            data={"tags": event.tags, "updated_on": event.updated_on},
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
            data={"tags": event.tags, "updated_on": event.updated_on},
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
            tags=[],  # tags already deleted in delete_tags_transactions
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

    def handle_bulk(self, item: dict) -> list[dict]:
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
                device_data=device_data,
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

        _device = unmarshall(item)
        return Device(**decompress_device_fields(_device))

    def query_by_tag(
        self,
        fields_to_drop: list[str] | set[str] = None,
        drop_tags_field=True,
        **kwargs,
    ) -> list[Device]:
        """
        Query the device by predefined tags, optionally dropping specific fields from the query result,
        noting that 'tags' field is dropped by default.

        Example:
            repository.query_by_tag(fields_to_drop=["field1", "field2"], foo="123", bar="456")
        """
        fields_to_drop = {
            *(fields_to_drop or []),
            *(["tags"] if drop_tags_field else []),
        }
        fields_to_return = Device.get_all_fields() - fields_to_drop

        dropped_mandatory_fields = Device.get_mandatory_fields() & fields_to_drop
        if dropped_mandatory_fields:
            raise CannotDropMandatoryFields(dropped_mandatory_fields)

        tag_value = DeviceTag(**kwargs).value
        pk = TableKey.DEVICE_TAG.key(tag_value)
        query_params = {
            "ExpressionAttributeValues": {":pk": marshall_value(pk)},
            "KeyConditionExpression": "pk = :pk",
            "TableName": self.table_name,
            **_dynamodb_projection_expression(fields_to_return),
        }

        response = self.client.query(**query_params)
        if "LastEvaluatedKey" in response:
            raise TooManyResults(f"Too many results for query '{kwargs}'")

        # Convert to Device, sorted by 'pk'
        compressed_devices = map(unmarshall, response["Items"])
        devices_as_dict = map(decompress_device_fields, compressed_devices)
        return [Device(**d) for d in sorted(devices_as_dict, key=lambda d: d["id"])]


def _dynamodb_projection_expression(updated_fields: list[str]):
    expression_attribute_names = {}
    update_clauses = []

    for field_name in updated_fields:
        field_name_placeholder = f"#{field_name}"

        update_clauses.append(field_name_placeholder)
        expression_attribute_names[field_name_placeholder] = field_name

    projection_expression = ", ".join(update_clauses)

    return dict(
        ProjectionExpression=projection_expression,
        ExpressionAttributeNames=expression_attribute_names,
    )
