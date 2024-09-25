from domain.core.cpm_system_id import CpmSystemId
from domain.core.cpm_system_id.v1 import CpmSystemIdType

from .keys.v3 import TableKey
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository


class CpmSystemIdRepository[T](Repository[T]):

    def __init__(self, table_name: str, model: type[T], dynamodb_client):
        super().__init__(
            table_name=table_name, model=model, dynamodb_client=dynamodb_client
        )

    def read(self, key_name: CpmSystemIdType) -> T:
        pk = TableKey.CPM_SYSTEM_ID.key(key_name)
        args = {"TableName": self.table_name, "Key": marshall(pk=pk, sk=pk)}
        result = self.client.get_item(**args)

        try:
            item = result["Item"]
        except KeyError:
            return self.model()  # return model with default values if not exists

        entry = unmarshall(item)
        return self.model(**entry)

    def create_or_update(self, key_name: CpmSystemIdType, new_number) -> CpmSystemId:
        pk = marshall_value(TableKey.CPM_SYSTEM_ID.key(key_name))
        item_key = {"pk": pk, "sk": pk}
        kwargs = {
            "TableName": self.table_name,
            "Key": item_key,
            "UpdateExpression": "SET latest_number = :new_value",
            "ExpressionAttributeValues": {
                ":new_value": marshall_value(new_number),
            },
        }
        result = self.client.update_item(**kwargs)
        return result
