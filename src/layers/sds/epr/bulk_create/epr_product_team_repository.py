from collections.abc import Generator
from typing import TYPE_CHECKING

from domain.core.product_team.v1 import ProductTeam
from domain.repository.device_reference_data_repository.v1 import QueryType
from domain.repository.keys.v1 import TableKey
from domain.repository.marshall import marshall, unmarshall
from sds.epr.constants import PRODUCT_TEAM_PREFIX

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient


class EprProductTeamRepository:

    def __init__(self, table_name, dynamodb_client: "DynamoDBClient"):
        self.table_name = table_name
        self.client = dynamodb_client

    def search(self, last_evaluated_key=None) -> Generator[ProductTeam, None, None]:
        sk_condition = QueryType.BEGINS_WITH.format("sk_read", ":sk_read")
        kwargs = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_read",
            "KeyConditionExpression": f"pk_read = :pk_read AND {sk_condition}",
            "ExpressionAttributeValues": marshall(
                **{
                    ":pk_read": TableKey.PRODUCT_TEAM.key(""),
                    ":sk_read": TableKey.PRODUCT_TEAM.key(PRODUCT_TEAM_PREFIX),
                }
            ),
        }
        if last_evaluated_key:
            kwargs["ExclusiveStartKey"] = last_evaluated_key

        result = self.client.query(**kwargs)
        yield from (ProductTeam(**item) for item in map(unmarshall, result["Items"]))

        if "LastEvaluatedKey" in result:
            yield from self.search(last_evaluated_key=result["LastEvaluatedKey"])
