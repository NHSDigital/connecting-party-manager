from attr import asdict
from domain.core.cpm_product.v1 import (
    CpmProduct,
    CpmProductCreatedEvent,
    CpmProductKeyAddedEvent,
)
from domain.core.product_key.v1 import ProductKey
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository.v2 import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
    update_transactions,
)


def create_product_index(
    table_name: str,
    product_data: dict,
    pk_key_parts: tuple[str],
    sk_key_parts: tuple[str],
    pk_table_key: TableKey = TableKey.PRODUCT_TEAM,
    sk_table_key: TableKey = TableKey.CPM_PRODUCT,
    root=False,
) -> TransactItem:
    pk = pk_table_key.key(*pk_key_parts)
    sk = sk_table_key.key(*sk_key_parts)
    return TransactItem(
        Put=TransactionStatement(
            TableName=table_name,
            Item=marshall(pk=pk, sk=sk, root=root, **product_data),
            ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
        )
    )


def _product_root_primary_key(product_team_id: str, product_id: str) -> dict:
    """
    Generates one fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary key (i.e. pk + sk) for the provided Device, indexed by the Device ID
    """
    pk = TableKey.PRODUCT_TEAM.key(product_team_id)
    sk = TableKey.CPM_PRODUCT.key(product_id)
    return marshall(pk=pk, sk=sk)


def _product_non_root_primary_keys(
    product_team_id: str, device_keys: list[ProductKey]
) -> list[dict]:
    """
    Generates all the fully marshalled (i.e. {"pk": {"S": "123"}} DynamoDB
    primary keys (i.e. pk + sk) for the provided Device. This is one primary key
    for every value of Device.keys and Device.tags
    """
    pk = TableKey.PRODUCT_TEAM.key(product_team_id)
    device_key_primary_keys = [
        marshall(pk=pk, sk=sk)
        for sk in (
            TableKey.CPM_PRODUCT.key(k.key_type, k.key_value) for k in device_keys
        )
    ]
    return device_key_primary_keys


def update_product_indexes(
    table_name: str,
    data: dict,
    product_team_id: str,
    product_id: str,
    keys: list[ProductKey],
):
    # Update the root product
    root_primary_key = _product_root_primary_key(
        product_team_id=product_team_id, product_id=product_id
    )
    update_root_product_transactions = update_transactions(
        table_name=table_name, primary_keys=[root_primary_key], data=data
    )
    # Update non-root products
    non_root_primary_keys = _product_non_root_primary_keys(
        product_team_id=product_team_id, device_keys=keys
    )
    update_non_root_devices_transactions = update_transactions(
        table_name=table_name, primary_keys=non_root_primary_keys, data=data
    )
    return update_root_product_transactions + update_non_root_devices_transactions


class CpmProductRepository(Repository[CpmProduct]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name, model=CpmProduct, dynamodb_client=dynamodb_client
        )

    def handle_CpmProductCreatedEvent(self, event: CpmProductCreatedEvent):
        return create_product_index(
            table_name=self.table_name,
            product_data=asdict(event),
            pk_key_parts=(event.product_team_id,),
            sk_key_parts=(event.id,),
            root=True,
        )

    def handle_CpmProductKeyAddedEvent(self, event: CpmProductKeyAddedEvent):
        # Create a copy of the Product indexed against the new key
        create_transaction = create_product_index(
            table_name=self.table_name,
            product_data=asdict(event),
            pk_key_parts=event.new_key.parts,
            sk_key_parts=event.new_key.parts,
            pk_table_key=TableKey.CPM_PRODUCT_KEY,
            sk_table_key=TableKey.CPM_PRODUCT_KEY,
        )

        # Update the value of "keys" on all other copies of this Device
        product_keys = {ProductKey(**key) for key in event.keys}
        product_keys_before_update = product_keys - {event.new_key}
        update_transactions = update_product_indexes(
            table_name=self.table_name,
            product_id=event.id,
            product_team_id=event.product_team_id,
            keys=product_keys_before_update,
            data={"keys": event.keys, "updated_on": event.updated_on},
        )
        return [create_transaction] + update_transactions

    def read(self, product_team_id: str, product_id: str) -> CpmProduct:
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
            raise ItemNotFound(product_team_id, product_id, item_type=CpmProduct)
        (item,) = items

        return CpmProduct(**item)

    def query_products_by_product_team(self, product_team_id) -> list[CpmProduct]:
        product_team_id = TableKey.PRODUCT_TEAM.key(product_team_id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND begins_with(sk, :sk_prefix)",
            "ExpressionAttributeValues": {
                ":pk": marshall_value(product_team_id),
                ":sk_prefix": marshall_value(f"{TableKey.CPM_PRODUCT}#"),
            },
        }
        response = self.client.query(**args)
        if "LastEvaluatedKey" in response:
            raise TooManyResults(f"Too many results for query '{kwargs}'")

        # Convert to Products
        if len(response["Items"]) > 0:
            products = map(unmarshall, response["Items"])
            return [CpmProduct(**p) for p in products]

        return []
