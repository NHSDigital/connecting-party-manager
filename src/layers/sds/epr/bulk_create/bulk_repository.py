import random
import time
from functools import wraps
from itertools import batched
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError
from domain.core.device.v1 import DeviceTag
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import (
    NON_ROOT_FIELDS_TO_COMPRESS,
    DeviceRepository,
    compress_device_fields,
)
from domain.repository.keys.v1 import KEY_SEPARATOR, TableKey
from domain.repository.marshall import marshall
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from domain.repository.transaction import TransactItem

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_dynamodb.type_defs import BatchWriteItemOutputTypeDef

RETRY_ERRORS = [
    "ProvisionedThroughputExceededException",
    "ThrottlingException",
    "InternalServerError",
]


def exponential_backoff_with_jitter(
    n_retries, base_delay=0.1, min_delay=0.05, max_delay=5
):
    """Calculate the delay with exponential backoff and jitter."""
    delay = min(base_delay * (2**n_retries), max_delay)
    return random.uniform(min_delay, delay)


def retry_with_jitter(max_retries=5, error=ClientError):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            exceptions = []
            while len(exceptions) < max_retries:
                try:
                    return func(*args, **kwargs)
                except error as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code not in RETRY_ERRORS:
                        raise
                    exceptions.append(e)
                delay = exponential_backoff_with_jitter(n_retries=len(exceptions))
                time.sleep(delay)
            raise ExceptionGroup(
                f"Failed to put item after {max_retries} retries", exceptions
            )

        return wrapped

    return wrapper


@retry_with_jitter()
def batch_write_chunk(
    client: "DynamoDBClient", table_name: str, chunk: list[dict]
) -> "BatchWriteItemOutputTypeDef":
    while chunk:
        _response = client.batch_write_item(RequestItems={table_name: chunk})
        chunk = _response["UnprocessedItems"].get(table_name)
    return _response


def create_index_batch(
    id: str,
    parent_key_parts: tuple[str],
    data: dict,
    root: bool,
    table_key: TableKey,
    parent_table_keys: tuple[TableKey],
) -> TransactItem:
    """
    Difference between `create_index` and `create_index_batch`:

    `create_index` is intended for the event-based
    handlers (e.g. `handle_XyzCreatedEvent`) which are called by the base
    `write` method, which expects `TransactItem`s for use with `client.transact_write_items`

    `create_index_batch` is intended for the entity-based handler
    `handle_bulk` which is called by the base method `write_bulk`, which expects
    `BatchWriteItem`s which we render as a `dict` for use with `client.batch_write_items`
    """

    write_key = table_key.key(id)
    read_key = KEY_SEPARATOR.join(
        table_key.key(_id)
        for table_key, _id in zip(parent_table_keys, parent_key_parts)
    )

    return {
        "PutRequest": {
            "Item": marshall(
                pk=write_key,
                sk=write_key,
                pk_read=read_key,
                sk_read=write_key,
                root=root,
                **data,
            ),
        },
    }


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


class BulkRepository:
    def __init__(self, table_name, dynamodb_client, batch_size=10):
        self.table_name = table_name
        self.client: "DynamoDBClient" = dynamodb_client
        self.batch_size = batch_size

        self.product_team_repository = ProductTeamRepository(
            table_name=None, dynamodb_client=None
        )
        self.product_repository = CpmProductRepository(
            table_name=None, dynamodb_client=None
        )
        self.device_repository = DeviceRepository(table_name=None, dynamodb_client=None)
        self.device_reference_data_repository = DeviceReferenceDataRepository(
            table_name=None, dynamodb_client=None
        )

    def generate_transaction_statements(
        self, item_with_name: dict[str, dict]
    ) -> list[dict]:
        ((object_type_name, item),) = item_with_name.items()
        handler_name = f"handle_{object_type_name}"
        handler = getattr(self, handler_name)
        statements = handler(item=item)
        if not isinstance(statements, list):
            statements = [statements]
        return statements

    def write(self, transaction_statements: list[dict]):
        responses = [
            batch_write_chunk(
                client=self.client, table_name=self.table_name, chunk=chunk
            )
            for chunk in batched(transaction_statements, self.batch_size)
        ]
        return responses

    def handle_ProductTeam(self, item: dict):
        parent_key = ("",)

        create_root_transaction = create_index_batch(
            id=item["id"],
            parent_key_parts=parent_key,
            data=item,
            root=True,
            table_key=self.product_team_repository.table_key,
            parent_table_keys=self.product_team_repository.parent_table_keys,
        )
        create_keys_transactions = [
            create_index_batch(
                id=key["key_value"],
                parent_key_parts=("",),
                data=item,
                root=False,
                table_key=self.product_team_repository.table_key,
                parent_table_keys=self.product_team_repository.parent_table_keys,
            )
            for key in item["keys"]
        ]
        return [create_root_transaction, *create_keys_transactions]

    def handle_CpmProduct(self, item: dict):
        parent_key_parts = (item["product_team_id"],)
        create_root_transaction = create_index_batch(
            id=item["id"],
            parent_key_parts=parent_key_parts,
            data=item,
            root=True,
            table_key=self.product_repository.table_key,
            parent_table_keys=self.product_repository.parent_table_keys,
        )
        create_keys_transactions = [
            create_index_batch(
                id=key["key_value"],
                parent_key_parts=parent_key_parts,
                data=item,
                root=False,
                table_key=self.product_repository.table_key,
                parent_table_keys=self.product_repository.parent_table_keys,
            )
            for key in item["keys"]
        ]
        return [create_root_transaction, *create_keys_transactions]

    def handle_Device(self, item: dict):
        parent_key = (
            item["product_team_id"],
            item["product_id"],
            item["environment"].upper(),
        )

        root_data = compress_device_fields(item)
        create_device_transaction = create_index_batch(
            id=item["id"],
            parent_key_parts=parent_key,
            data=root_data,
            root=True,
            table_key=self.device_repository.table_key,
            parent_table_keys=self.device_repository.parent_table_keys,
        )

        non_root_data = compress_device_fields(
            item, fields_to_compress=NON_ROOT_FIELDS_TO_COMPRESS
        )
        create_keys_transactions = [
            create_index_batch(
                id=key["key_value"],
                parent_key_parts=parent_key,
                data=non_root_data,
                root=False,
                table_key=self.device_repository.table_key,
                parent_table_keys=self.device_repository.parent_table_keys,
            )
            for key in item["keys"]
        ]

        create_tags_transactions = [
            create_tag_index_batch(
                device_id=item["id"],
                tag_value=DeviceTag(__root__=tag).value,
                data=non_root_data,
            )
            for tag in item["tags"]
        ]
        return (
            [create_device_transaction]
            + create_keys_transactions
            + create_tags_transactions
        )

    def handle_DeviceReferenceData(self, item: dict):
        create_root_transaction = create_index_batch(
            id=item["id"],
            parent_key_parts=(
                item["product_team_id"],
                item["product_id"],
                item["environment"].upper(),
            ),
            data=item,
            root=True,
            table_key=self.device_reference_data_repository.table_key,
            parent_table_keys=self.device_reference_data_repository.parent_table_keys,
        )
        return [create_root_transaction]
