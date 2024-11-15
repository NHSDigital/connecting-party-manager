from attr import asdict
from domain.core.product_team.v3 import ProductTeam, ProductTeamCreatedEvent
from domain.core.product_team_key import ProductTeamKey
from domain.repository.keys.v3 import TableKey
from domain.repository.repository.v3 import Repository


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
        return super()._read(parent_ids=(), id=id)

    def handle_ProductTeamCreatedEvent(self, event: ProductTeamCreatedEvent):
        create_root_transaction = self.create_index(
            id=event.id, parent_key_parts=(event.id,), data=asdict(event), root=True
        )

        keys = {ProductTeamKey(**key) for key in event.keys}
        create_key_transactions = [
            self.create_index(
                id=key.key_value,
                parent_key_parts=(key.key_value,),
                data=asdict(event),
                root=True,
            )
            for key in keys
        ]

        return [create_root_transaction] + create_key_transactions
