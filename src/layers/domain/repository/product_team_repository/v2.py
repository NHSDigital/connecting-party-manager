from attr import asdict
from domain.core.product_team.v3 import ProductTeam, ProductTeamCreatedEvent
from domain.repository.errors import ItemNotFound
from domain.repository.keys import TableKeys
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=ProductTeam, dynamodb_client=dynamodb_client
        )

    def handle_ProductTeamCreatedEvent(self, event: ProductTeamCreatedEvent):
        pk = TableKeys.PRODUCT_TEAM.key(event.id)
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=pk, **asdict(event)),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def read(self, id) -> ProductTeam:
        pk = TableKeys.PRODUCT_TEAM.key(id)
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
            raise ItemNotFound(key=id)
        (item,) = items

        return ProductTeam(**item)
