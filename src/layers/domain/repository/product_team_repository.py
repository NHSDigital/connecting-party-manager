from dataclasses import asdict

from domain.core.product_team import (
    ProductTeam,
    ProductTeamCreatedEvent,
    ProductTeamDeletedEvent,
)

from .errors import ItemNotFound
from .keys import TableKeys
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=ProductTeam, dynamodb_client=dynamodb_client
        )

    def handle_ProductTeamCreatedEvent(
        self, event: ProductTeamCreatedEvent, entity: ProductTeam
    ):
        pk = TableKeys.PRODUCT_TEAM.key(event.id)
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(pk=pk, sk=pk, **asdict(event)),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_ProductTeamDeletedEvent(
        self, event: ProductTeamDeletedEvent, entity: ProductTeam
    ):
        pk = TableKeys.PRODUCT_TEAM.key(event.id)
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(pk=pk, sk=pk),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

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
