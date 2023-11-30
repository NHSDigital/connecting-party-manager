from domain.core.product import (
    Product,
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductKey,
    ProductKeyAddedEvent,
    ProductKeyRemovedEvent,
    ProductUpdatedEvent,
    Relationship,
    RelationshipAddedEvent,
    RelationshipRemovedEvent,
)
from repository.keys import ods_pk, product_key_sk, product_pk, product_relationship_sk

from .errors import NotFoundException
from .repository import Repository
from .utils import marshall, unmarshall


class ProductRepository(Repository[Product]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Product, dynamodb_client=dynamodb_client
        )

    def handle_ProductCreatedEvent(self, event: ProductCreatedEvent, entity: Product):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_pk(event.id),
                        "pk_1": ods_pk(event.ods_code),
                        "sk_1": product_pk(event.id),
                        "name": event.name,
                        "type": event.type,
                        "ods_code": event.ods_code,
                        "ods_name": event.ods_name,
                        "product_team_id": event.product_team_id,
                        "status": event.status,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_ProductUpdatedEvent(self, event: ProductUpdatedEvent, entity: Product):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_pk(event.id),
                        "name": event.name,
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_ProductDeletedEvent(self, event: ProductDeletedEvent, entity: Product):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_pk(event.id),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_RelationshipAddedEvent(
        self, event: RelationshipAddedEvent, entity: Product
    ):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_relationship_sk(event.target),
                        "pk_1": product_relationship_sk(event.target),
                        "sk_1": product_pk(event.id),
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_RelationshipRemovedEvent(
        self, event: RelationshipRemovedEvent, entity: Product
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_relationship_sk(event.target),
                    }
                ),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def handle_ProductKeyAddedEvent(self, event: ProductKeyAddedEvent, entity: Product):
        return {
            "Put": {
                "TableName": self.table_name,
                "Item": marshall(
                    {
                        "pk": product_pk(event.id),
                        "sk": product_key_sk(event.key),
                        "pk_1": product_key_sk(event.key),
                        "sk_1": product_key_sk(event.key),
                        "type": event.type,
                    }
                ),
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }

    def handle_ProductKeyRemovedEvent(
        self, event: ProductKeyRemovedEvent, entity: Product
    ):
        return {
            "Delete": {
                "TableName": self.table_name,
                "Key": marshall({"pk": f"P#{event.id}", "sk": f"PK#{event.key}"}),
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        }

    def read_by_key(self, key) -> Product:
        pk_1 = product_key_sk(key)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1 AND sk_1 = :pk_1",
            "ExpressionAttributeValues": {":pk_1": {"S": pk_1}},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise NotFoundException(key=key)

        (item,) = items

        return self.read(item["pk"].split("#", 1)[1])

    def read(self, id) -> Product:
        pk = f"P#{id}"
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": {"S": pk}},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]

        keys = [v for v in items if v["sk"].startswith("PK#")]
        relationships = [v for v in items if v["sk"].startswith("PR#")]
        product = [v for v in items if v["sk"].startswith("P#")][0]

        return Product(
            id=id,
            relationships={
                r["sk"].split("#", 1)[1]: Relationship(**r) for r in relationships
            },
            keys={k["sk"].split("#", 1)[1]: ProductKey(**k) for k in keys},
            **product,
        )
