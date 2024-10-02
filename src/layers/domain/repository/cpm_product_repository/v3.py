from attr import asdict
from domain.core.cpm_product.v1 import CpmProduct, CpmProductCreatedEvent
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)


class CpmProductRepository(Repository[CpmProduct]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=CpmProduct, dynamodb_client=dynamodb_client
        )

    def handle_CpmProductCreatedEvent(self, event: CpmProductCreatedEvent):
        pk = TableKey.PRODUCT_TEAM.key(event.product_team_id)
        sk = TableKey.CPM_PRODUCT.key(event.id)
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=sk, **asdict(event)),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def read(self, product_team_id, product_id) -> CpmProduct:
        pk = TableKey.PRODUCT_TEAM.key(product_team_id)
        sk = TableKey.CPM_PRODUCT.key(product_id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND sk = :sk",
            "ExpressionAttributeValues": {
                ":pk": marshall_value(pk),
                ":sk": marshall_value(sk),
            },
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(key=product_id)

        (item,) = items

        return CpmProduct(**item)
