from attr import asdict
from domain.core.enum import EntityType
from domain.core.product_team import (
    ProductTeam,
    ProductTeamCreatedEvent,
    ProductTeamDeletedEvent,
)
from domain.core.product_team_key import ProductTeamKey
from domain.repository.cpm_repository import Repository
from domain.repository.keys import TableKey


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=ProductTeam,
            dynamodb_client=dynamodb_client,
            table_key=TableKey.PRODUCT_TEAM,
            parent_table_keys=(TableKey.PRODUCT_TEAM,),
        )

    def read(self, id: str) -> ProductTeam:
        return super()._read(parent_ids=(id,), id=id, status="active")

    def search(self) -> list[ProductTeam]:
        return super()._search(parent_ids=("",))

    def handle_ProductTeamCreatedEvent(self, event: ProductTeamCreatedEvent):
        create_root_transaction = self.create_index(
            id=event.id,
            parent_key_parts=(event.id,),
            data=asdict(event),
            root=True,
            row_type=EntityType.PRODUCT_TEAM,
        )

        keys = {ProductTeamKey(**key) for key in event.keys}
        create_key_transactions = [
            self.create_index(
                id=key.key_value,
                parent_key_parts=(key.key_value,),
                data=asdict(event),
                root=False,
                row_type=EntityType.PRODUCT_TEAM_ALIAS,
            )
            for key in keys
        ]

        return [create_root_transaction] + create_key_transactions

    def handle_ProductTeamDeletedEvent(self, event: ProductTeamDeletedEvent):
        return self.update_indexes(
            pk=TableKey.PRODUCT_TEAM.key(event.id),
            id=event.id,
            keys=event.keys,
            data=asdict(event),
        )
