from copy import copy

from attr import asdict
from domain.core.device import Device as _Device
from domain.core.device import (
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceReferenceDataIdAddedEvent,
    DeviceTag,
    DeviceTagAddedEvent,
    DeviceTagsAddedEvent,
    DeviceTagsClearedEvent,
    DeviceUpdatedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key import DeviceKey
from domain.core.enum import Status
from domain.core.event import Event
from domain.repository.compression import pkl_dumps_gzip, pkl_loads_gzip
from domain.repository.keys import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository import Repository, TooManyResults
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
    dynamodb_projection_expression,
    update_transactions,
)
from pydantic import validator

TAGS = "tags"
ROOT_FIELDS_TO_COMPRESS = [TAGS]
NON_ROOT_FIELDS_TO_COMPRESS = ["questionnaire_responses"]
BATCH_GET_SIZE = 100


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


def create_tag_index(
    table_name: str, device_id: str, tag_value: str, data: dict
) -> TransactItem:
    pk = TableKey.DEVICE_TAG.key(tag_value)
    sk = TableKey.DEVICE.key(device_id)
    return TransactItem(
        Put=TransactionStatement(
            TableName=table_name,
            Item=marshall(pk=pk, sk=sk, pk_read=pk, sk_read=sk, root=False, **data),
            ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
        )
    )


def create_tag_index_batch(device_id: str, tag_value: str, data: dict):
    """
    Difference between `create_tag_index` and `create_tag_index_batch`:

    `create_index` is intended for the event-based
    `handle_TagAddedEvent` which is called by the base
    `write` method, which expects `TransactItem`s for use with `client.transact_write_items`

    `create_tag_index_batch` is intended for the entity-based handler
    `handle_bulk` which is called by the base method `write_bulk`, which expects
    `BatchWriteItem`s which we render as a `dict` for use with `client.batch_write_items`
    """
    pk = TableKey.DEVICE_TAG.key(tag_value)
    sk = TableKey.DEVICE.key(device_id)
    return {
        "PutRequest": {
            "Item": marshall(pk=pk, sk=sk, pk_read=pk, sk_read=sk, root=False, **data)
        }
    }


def delete_tag_index(table_name: str, device_id: str, tag_value: str) -> TransactItem:
    pk = TableKey.DEVICE_TAG.key(tag_value)
    sk = TableKey.DEVICE.key(device_id)
    return TransactItem(
        Delete=TransactionStatement(
            TableName=table_name,
            Key=marshall(pk=pk, sk=sk),
            ConditionExpression=ConditionExpression.MUST_EXIST,
        )
    )


def update_tag_indexes(
    table_name: str, device_id: str, tag_values: list[str], data: dict
) -> TransactItem:
    root_pk = TableKey.DEVICE.key(device_id)
    tag_keys = [
        marshall(pk=TableKey.DEVICE_TAG.key(tag_value), sk=root_pk)
        for tag_value in tag_values
    ]
    return update_transactions(table_name=table_name, primary_keys=tag_keys, data=data)


class Device(_Device):
    """Wrapper around domain Device that also deserialises tags"""

    @validator("tags", pre=True)
    def deserialise_tags(cls, tags):
        if isinstance(tags, str):
            tags = [pkl_loads_gzip(tag) for tag in pkl_loads_gzip(tags)]
        return tags


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=Device,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM, TableKey.CPM_PRODUCT),
            table_key=TableKey.DEVICE,
        )

    def read(self, product_team_id: str, product_id: str, id: str):
        return super()._read(parent_ids=(product_team_id, product_id), id=id)

    def search(self, product_team_id: str, product_id: str):
        return super()._query(parent_ids=(product_team_id, product_id))

    def handle_DeviceCreatedEvent(self, event: DeviceCreatedEvent) -> TransactItem:
        return self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id, event.product_id),
            data=compress_device_fields(event),
            root=True,
        )

    def handle_DeviceUpdatedEvent(
        self, event: DeviceUpdatedEvent
    ) -> list[TransactItem]:
        root_pk = self.table_key.key(event.id)
        (root_transaction,) = update_transactions(
            table_name=self.table_name,
            primary_keys=[marshall(pk=root_pk, sk=root_pk)],
            data=compress_device_fields(event),
        )

        non_root_data = compress_device_fields(
            event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )

        key_pks = (self.table_key.key(DeviceKey(**k).key_value) for k in event.keys)
        key_transactions = update_transactions(
            table_name=self.table_name,
            primary_keys=[marshall(pk=pk, sk=pk) for pk in key_pks],
            data=non_root_data,
        )

        tag_transactions = update_tag_indexes(
            table_name=self.table_name,
            device_id=event.id,
            tag_values=event.tags,
            data=non_root_data,
        )

        return [root_transaction] + key_transactions + tag_transactions

    def handle_DeviceDeletedEvent(
        self, event: DeviceDeletedEvent
    ) -> list[TransactItem]:
        # Inactive Devices have tags removed so that they are
        # no longer searchable
        tag_delete_transactions = [
            delete_tag_index(
                table_name=self.table_name,
                device_id=event.id,
                tag_value=tag,
            )
            for tag in event.deleted_tags
        ]

        # Prepare data for the inactive copies
        inactive_data = compress_device_fields(event)
        inactive_data["status"] = str(Status.INACTIVE)

        # Collect keys for the original devices
        original_keys = {DeviceKey(**key).key_value for key in event.keys}

        # Create copy of original device and indexes with new pk and sk
        root_copy_transaction = self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id, event.product_id),
            data=inactive_data,
            table_key=TableKey.DEVICE_STATUS,
            root=True,
        )

        # Create delete transactions for original device and key indexes
        root_delete_transaction = self.delete_index(event.id)
        key_delete_transactions = [self.delete_index(key) for key in original_keys]

        return (
            tag_delete_transactions
            + [root_copy_transaction, root_delete_transaction]
            + key_delete_transactions
        )

    def handle_DeviceKeyAddedEvent(
        self, event: DeviceKeyAddedEvent
    ) -> list[TransactItem]:
        # Create a copy of the Device indexed against the new key
        _non_root_data = compress_device_fields(
            event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )
        create_key_transaction = self.create_index(
            id=event.new_key.key_value,
            parent_key_parts=(event.product_team_id, event.product_id),
            data=_non_root_data,
            root=False,
        )

        data = {"keys": event.keys, "updated_on": event.updated_on}

        # Update "keys" on the root and key-indexed Devices
        device_keys = {DeviceKey(**key).key_value for key in event.keys}
        device_keys_before_update = device_keys - {event.new_key.key_value}
        update_root_and_key_transactions = self.update_indexes(
            id=event.id, keys=device_keys_before_update, data=data
        )

        # Update "keys" on the tag-indexed Devices
        update_tag_transactions = update_tag_indexes(
            table_name=self.table_name,
            device_id=event.id,
            tag_values=event.tags,
            data=data,
        )

        return (
            [create_key_transaction]
            + update_root_and_key_transactions
            + update_tag_transactions
        )

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> list[TransactItem]:
        delete_key_transaction = self.delete_index(event.deleted_key.key_value)

        data = {"keys": event.keys, "updated_on": event.updated_on}

        # Update "keys" on the root and key-indexed Devices
        device_keys = {DeviceKey(**key).key_value for key in event.keys}
        device_keys_before_update = device_keys - {event.deleted_key.key_value}
        update_root_and_key_transactions = self.update_indexes(
            id=event.id, keys=device_keys_before_update, data=data
        )

        # Update "keys" on the tag-indexed Devices
        update_tag_transactions = update_tag_indexes(
            table_name=self.table_name,
            device_id=event.id,
            tag_values=event.tags,
            data=data,
        )

        return (
            [delete_key_transaction]
            + update_root_and_key_transactions
            + update_tag_transactions
        )

    def handle_DeviceTagAddedEvent(
        self, event: DeviceTagAddedEvent
    ) -> list[TransactItem]:
        data = {"tags": event.tags, "updated_on": event.updated_on}

        # Create a copy of the Device indexed against the new tag
        create_tag_transaction = create_tag_index(
            table_name=self.table_name,
            device_id=event.id,
            tag_value=event.new_tag,
            data=compress_device_fields(
                event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
            ),
        )

        # Update "tags" on the root and key-indexed Devices
        device_keys = {DeviceKey(**key).key_value for key in event.keys}
        update_root_and_key_transactions = self.update_indexes(
            id=event.id, keys=device_keys, data=data
        )

        # Update "tags" on the tag-indexed Devices
        update_tag_transactions = update_tag_indexes(
            table_name=self.table_name,
            device_id=event.id,
            tag_values=event.tags,
            data=data,
        )

        return (
            [create_tag_transaction]
            + update_root_and_key_transactions
            + update_tag_transactions
        )

    def handle_DeviceTagsAddedEvent(self, event: DeviceTagsAddedEvent):
        data = {"tags": event.tags, "updated_on": event.updated_on}
        _data = compress_device_fields(
            event, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )

        # Create a copy of the Device indexed against the new tag
        create_tag_transactions = [
            create_tag_index(
                table_name=self.table_name,
                device_id=event.id,
                tag_value=tag,
                data=_data,
            )
            for tag in event.new_tags
        ]

        # Update "tags" on the root and key-indexed Devices
        device_keys = {DeviceKey(**key).key_value for key in event.keys}
        update_root_and_key_transactions = self.update_indexes(
            id=event.id, keys=device_keys, data=data
        )

        # Update "tags" on the tag-indexed Devices
        update_tag_transactions = update_tag_indexes(
            table_name=self.table_name,
            device_id=event.id,
            tag_values=set(event.tags) - set(event.new_tags),
            data=data,
        )

        return (
            create_tag_transactions
            + update_root_and_key_transactions
            + update_tag_transactions
        )

    def handle_DeviceTagsClearedEvent(self, event: DeviceTagsClearedEvent):
        delete_tags_transactions = [
            delete_tag_index(
                table_name=self.table_name,
                device_id=event.id,
                tag_value=tag,
            )
            for tag in event.deleted_tags
        ]

        keys = {DeviceKey(**key).key_value for key in event.keys}
        update_transactions = self.update_indexes(
            id=event.id, keys=keys, data={"tags": []}
        )
        return delete_tags_transactions + update_transactions

    def handle_DeviceReferenceDataIdAddedEvent(
        self, event: DeviceReferenceDataIdAddedEvent
    ) -> TransactItem:
        pk = TableKey.DEVICE.key(event.id)
        data = asdict(event)
        data.pop("id")
        return update_transactions(
            table_name=self.table_name, primary_keys=[marshall(pk=pk, sk=pk)], data=data
        )

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ) -> TransactItem:
        data = asdict(event)
        data.pop("id")
        return self.update_indexes(id=event.id, keys=[], data=data)

    def handle_bulk(self, item: dict) -> list[dict]:
        parent_key = (item["product_team_id"], item["product_id"])

        root_data = compress_device_fields(item)
        create_device_transaction = self.create_index_batch(
            id=item["id"], parent_key_parts=parent_key, data=root_data, root=True
        )

        non_root_data = compress_device_fields(
            item, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )
        create_keys_transactions = [
            self.create_index_batch(
                id=key["key_value"],
                parent_key_parts=parent_key,
                data=non_root_data,
                root=False,
            )
            for key in item["keys"]
        ]

        create_tags_transactions = [
            create_tag_index_batch(
                device_id=item["id"], tag_value=tag, data=non_root_data
            )
            for tag in item["tags"]
        ]
        return (
            [create_device_transaction]
            + create_keys_transactions
            + create_tags_transactions
        )

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
            **dynamodb_projection_expression(fields_to_return),
        }

        response = self.client.query(**query_params)
        if "LastEvaluatedKey" in response:
            raise TooManyResults(f"Too many results for query '{kwargs}'")

        # Convert to Device, sorted by 'pk'
        compressed_devices = map(unmarshall, response["Items"])
        devices_as_dict = map(decompress_device_fields, compressed_devices)
        return [Device(**d) for d in sorted(devices_as_dict, key=lambda d: d["id"])]


class InactiveDeviceRepository(Repository[Device]):
    """Read-only repository"""

    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=Device,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM, TableKey.CPM_PRODUCT),
            table_key=TableKey.DEVICE_STATUS,
        )

    def read(self, product_team_id: str, product_id: str, id: str):
        return self._read(parent_ids=(product_team_id, product_id), id=id)
