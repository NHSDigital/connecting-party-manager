from itertools import chain
from typing import TYPE_CHECKING

from domain.core.device.v1 import DeviceEventDeserializer
from domain.core.device_reference_data.v1 import DeviceReferenceDataEventDeserializer
from domain.core.epr_product.v1 import EprProductEventDeserializer
from domain.core.product_team.v1 import ProductTeamEventDeserializer
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.epr_product_repository.v1 import EprProductRepository
from domain.repository.product_team_epr_repository.v1 import ProductTeamRepository
from domain.repository.repository.v1 import (
    BATCH_SIZE,
    Repository,
    _split_transactions_by_key,
    transact_write_chunk,
)
from sds.epr.updates.etl_device import EtlDeviceEventDeserializer
from sds.epr.updates.etl_device_repository import EtlDeviceRepository

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient


def generate_transaction_statements(repository_class: type[Repository], event):
    handler_name = f"handle_{type(event).__name__}"
    handler = getattr(repository_class, handler_name)
    transact_items = handler(event=event)

    if not isinstance(transact_items, list):
        transact_items = [transact_items]

    return transact_items


class EtlUpdateRepository:
    def __init__(self, table_name, dynamodb_client):
        self.table_name = table_name
        self.client: "DynamoDBClient" = dynamodb_client
        self.repository_lookup = {
            ProductTeamEventDeserializer: ProductTeamRepository(
                table_name=table_name, dynamodb_client=dynamodb_client
            ),
            EprProductEventDeserializer: EprProductRepository(
                table_name=table_name, dynamodb_client=dynamodb_client
            ),
            DeviceEventDeserializer: DeviceRepository(
                table_name=table_name, dynamodb_client=dynamodb_client
            ),
            DeviceReferenceDataEventDeserializer: DeviceReferenceDataRepository(
                table_name=table_name, dynamodb_client=dynamodb_client
            ),
            EtlDeviceEventDeserializer: EtlDeviceRepository(
                table_name=table_name, dynamodb_client=dynamodb_client
            ),
        }

    def write(self, events, batch_size=BATCH_SIZE):
        transact_items = chain.from_iterable(
            (
                generate_transaction_statements(
                    repository_class=self.repository_lookup[deserializer_class],
                    event=event,
                )
                for deserializer_class, event in events
            )
        )

        responses = [
            transact_write_chunk(client=self.client, chunk=transact_item_chunk)
            for transact_item_chunk in _split_transactions_by_key(
                transact_items, batch_size
            )
        ]
        return responses
