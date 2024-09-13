from attr import asdict
from domain.core.product_team.v3 import ProductTeam, ProductTeamCreatedEvent
from domain.core.product_team_key import ProductTeamKey
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)


def create_product_team_index(
    table_name: str,
    product_team_data: dict,
    pk_key_parts: tuple[str],
    sk_key_parts: tuple[str],
    pk_table_key: TableKey = TableKey.PRODUCT_TEAM,
    sk_table_key: TableKey = TableKey.PRODUCT_TEAM,
    root=False,
) -> TransactItem:
    pk = pk_table_key.key(*pk_key_parts)
    sk = sk_table_key.key(*sk_key_parts)
    return TransactItem(
        Put=TransactionStatement(
            TableName=table_name,
            Item=marshall(pk=pk, sk=sk, root=root, **product_team_data),
            ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
        )
    )


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=ProductTeam, dynamodb_client=dynamodb_client
        )

    def handle_ProductTeamCreatedEvent(self, event: ProductTeamCreatedEvent):
        create_transaction = create_product_team_index(
            table_name=self.table_name,
            product_team_data=asdict(event),
            pk_key_parts=(event.id,),
            sk_key_parts=(event.id,),
            root=True,
        )

        product_team_keys = {ProductTeamKey(**key) for key in event.keys}
        transactions = []
        for product_team_key in product_team_keys:
            key_type = (
                product_team_key.key_type.replace("_", " ").title().replace(" ", "")
            )
            create_key_transaction = create_product_team_index(
                table_name=self.table_name,
                product_team_data=asdict(event),
                pk_key_parts=(
                    key_type,
                    product_team_key.key_value,
                ),
                sk_key_parts=(
                    key_type,
                    product_team_key.key_value,
                ),
                pk_table_key=TableKey.PRODUCT_TEAM_KEY,
                sk_table_key=TableKey.PRODUCT_TEAM_KEY,
            )
            transactions.append(create_key_transaction)

        return [create_transaction] + transactions

    def read(self, id) -> ProductTeam:
        pk = TableKey.PRODUCT_TEAM.key(id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND sk = :sk",
            "ExpressionAttributeValues": {
                ":pk": marshall_value(pk),
                ":sk": marshall_value(pk),
            },
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(id, item_type=ProductTeam)
        (item,) = items

        return ProductTeam(**item)
