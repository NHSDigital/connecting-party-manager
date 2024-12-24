from enum import StrEnum

from attr import asdict
from domain.core.device_reference_data import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.repository.keys import TableKey
from domain.repository.repository import Repository
from domain.repository.transaction import TransactItem


class QueryType(StrEnum):
    EQUALS = "{} = {}"
    BEGINS_WITH = "begins_with({}, {})"


class DeviceReferenceDataRepository(Repository[DeviceReferenceData]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=DeviceReferenceData,
            dynamodb_client=dynamodb_client,
            table_key=TableKey.DEVICE_REFERENCE_DATA,
            parent_table_keys=(
                TableKey.PRODUCT_TEAM,
                TableKey.CPM_PRODUCT,
                TableKey.ENVIRONMENT,
            ),
        )

    def read(self, product_team_id: str, product_id: str, environment: str, id: str):
        return super()._read(
            parent_ids=(product_team_id, product_id, environment.upper()), id=id
        )

    def search(self, product_team_id: str, product_id: str, environment: str):
        return super()._search(
            parent_ids=(product_team_id, product_id, environment.upper())
        )

    def handle_DeviceReferenceDataCreatedEvent(
        self, event: DeviceReferenceDataCreatedEvent
    ) -> TransactItem:
        environment = event.environment
        return self.create_index(
            id=event.id,
            parent_key_parts=(
                event.product_team_id,
                event.product_id,
                environment.upper(),
            ),
            data=asdict(event),
            root=True,
        )

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ) -> TransactItem:
        data = asdict(event)
        data.pop("id")
        return self.update_indexes(id=event.id, keys=[], data=data)
