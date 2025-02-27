from attr import asdict
from domain.core.product_team_epr import ProductTeam, ProductTeamCreatedEvent
from domain.core.product_team_key import ProductTeamKey
from domain.repository.keys import TableKey
from domain.repository.repository import Repository


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
        return super()._read(parent_ids=("",), id=id)

    def search(self) -> list[ProductTeam]:
        return super()._search(parent_ids=("",))

    def handle_ProductTeamCreatedEvent(self, event: ProductTeamCreatedEvent):
        create_root_transaction = self.create_index(
            id=event.id, parent_key_parts=("",), data=asdict(event), root=True
        )

        keys = {ProductTeamKey(**key) for key in event.keys}
        create_key_transactions = [
            self.create_index(
                id=key.key_value,
                parent_key_parts=("",),
                data=asdict(event),
                root=False,
            )
            for key in keys
        ]

        return [create_root_transaction] + create_key_transactions
