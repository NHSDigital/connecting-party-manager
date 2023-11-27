from domain.core.product_team import (
    ProductTeam,
    ProductTeamCreatedEvent,
    ProductTeamDeletedEvent,
)

from .repository import Repository
from .utils import marshall, unmarshall


class ProductTeamRepository(Repository[ProductTeam]):
    def __init__(self, table_name):
        super().__init__(table_name=table_name, model=ProductTeam)

    def handle_ProductTeamCreatedEvent(
        self, event: ProductTeamCreatedEvent, entity: ProductTeam
    ):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": f"T#{event.id}",
                        "sk": f"T#{event.id}",
                        "pk_1": f"O#{event.ods_code}",
                        "sk_1": f"T#{event.id}",
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
                        "pk": f"T#{event.id}",
                        "sk": f"T#{event.id}",
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def read(self, id) -> ProductTeam:
        pk = f"T#{id}"
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND sk = :sk",
            "ExpressionAttributeValues": {
                ":pk": {"S": pk},
                ":sk": {"S": pk},
            },
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        (item,) = items

        return ProductTeam(id=id, **item)
