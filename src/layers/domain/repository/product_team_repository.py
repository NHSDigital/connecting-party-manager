from domain.core.product_team import (
    ProductTeam,
    ProductTeamCreatedEvent,
    ProductTeamDeletedEvent,
)

from .errors import NotFoundException
from .keys import ods_pk, product_team_pk
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
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": product_team_pk(event.id),
                        "sk": product_team_pk(event.id),
                        "pk_1": ods_pk(event.ods_code),
                        "sk_1": product_team_pk(event.id),
                        "name": event.name,
                        "ods_code": event.ods_code,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_ProductTeamDeletedEvent(
        self, event: ProductTeamDeletedEvent, entity: ProductTeam
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": product_team_pk(event.id),
                        "sk": product_team_pk(event.id),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def read(self, id) -> ProductTeam:
        pk = product_team_pk(id)
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

        return ProductTeam(id=id, **item)
