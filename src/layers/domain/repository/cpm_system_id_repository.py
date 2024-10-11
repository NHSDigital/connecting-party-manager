from domain.core.cpm_system_id import CpmSystemId

from .keys.v3 import TableKey
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository


class CpmSystemIdRepository[T](Repository[T]):

    def __init__(self, table_name: str, model: type[T], dynamodb_client):
        super().__init__(
            table_name=table_name, model=model, dynamodb_client=dynamodb_client
        )

    def read(self) -> T:
        pk = TableKey.CPM_SYSTEM_ID.key(self.model.__name__)
        args = {"TableName": self.table_name, "Key": marshall(pk=pk, sk=pk)}
        result = self.client.get_item(**args)

        try:
            item = result["Item"]
        except KeyError:
            return self.model()  # return model with default values if not exists

        entry = unmarshall(item)
        return self.model(__root__=entry["latest_system_id"])

    def create_or_update(self, new_cpm_system_id) -> CpmSystemId:
        pk = marshall_value(TableKey.CPM_SYSTEM_ID.key(self.model.__name__))
        item_key = {"pk": pk, "sk": pk}
        kwargs = {
            "TableName": self.table_name,
            "Key": item_key,
            "UpdateExpression": "SET latest_system_id = :new_value",
            "ExpressionAttributeValues": {
                ":new_value": marshall_value(new_cpm_system_id),
            },
        }
        result = self.client.update_item(**kwargs)
        return result
