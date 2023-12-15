from dataclasses import asdict

from domain.core.product_team import ProductTeam, ProductTeamCreatedEvent

from .errors import NotFoundException
from .keys import TableKeys
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository
from .transaction import ConditionExpression, TransactionItem, TransactionStatement


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=ProductTeam, dynamodb_client=dynamodb_client
        )

    def handle_ProductTeamCreatedEvent(
        self, event: ProductTeamCreatedEvent, entity: ProductTeam
    ):
        pk = TableKeys.PRODUCT_TEAM.key(event.id)
        return TransactionItem(
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
            raise NotFoundException(key=id)
        (item,) = items

        return ProductTeam(**item)
