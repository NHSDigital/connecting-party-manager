from domain.core.cpm_system_id import CpmSystemId

from .keys.v3 import TableKey
from .marshall import marshall, unmarshall
from .repository import Repository


class CpmSystemIdRepository(Repository[CpmSystemId]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=CpmSystemId, dynamodb_client=dynamodb_client
        )

    def read(self, key_name) -> CpmSystemId:
        pk = f"{TableKey.CPM_SYSTEM_ID}#{key_name}"
        args = {"TableName": self.table_name, "Key": marshall(pk=pk, sk=pk)}
        result = self.client.get_item(**args)

        try:
            item = result["Item"]
        except KeyError:
            return None

        entry = unmarshall(item)
        return entry

    def create_or_update(self, key_name, new_number) -> CpmSystemId:
        pk = f"{TableKey.CPM_SYSTEM_ID}#{key_name}"
        item_key = {
            "pk": {"S": f"{pk}"},
            "sk": {"S": f"{pk}"},
        }
        args = {
            "TableName": self.table_name,
            "Key": item_key,
            "UpdateExpression": "SET latest = :new_value",
            "ExpressionAttributeValues": {
                ":new_value": {"N": str(new_number)},
            },
        }
        result = self.client.update_item(**args)
        return result
