from contextlib import contextmanager
from typing import Generator

from event.aws.client import dynamodb_client
from moto import mock_aws
from mypy_boto3_dynamodb import DynamoDBClient

CHUNK_SIZE = 100

KEY_SCHEMAS = [
    {"AttributeName": "pk", "KeyType": "HASH"},
    {"AttributeName": "sk", "KeyType": "RANGE"},
]
GLOBAL_SECONDARY_INDEXES_CPM = [
    {
        "IndexName": "idx_gsi_read_1",
        "KeySchema": [
            {"AttributeName": "pk_read_1", "KeyType": "HASH"},
            {"AttributeName": "sk_read_1", "KeyType": "RANGE"},
        ],
        "Projection": {"ProjectionType": "ALL"},
    },
    {
        "IndexName": "idx_gsi_read_2",
        "KeySchema": [
            {"AttributeName": "pk_read_2", "KeyType": "HASH"},
            {"AttributeName": "sk_read_2", "KeyType": "RANGE"},
        ],
        "Projection": {"ProjectionType": "ALL"},
    },
]
ATTRIBUTE_DEFINITIONS_CPM = [
    {"AttributeName": "pk", "AttributeType": "S"},
    {"AttributeName": "sk", "AttributeType": "S"},
    {"AttributeName": "pk_read_1", "AttributeType": "S"},
    {"AttributeName": "sk_read_1", "AttributeType": "S"},
    {"AttributeName": "pk_read_2", "AttributeType": "S"},
    {"AttributeName": "sk_read_2", "AttributeType": "S"},
]


def _scan(client: DynamoDBClient, table_name: str) -> Generator[dict, None, None]:
    start_key_kwargs = {}
    while True:
        response = client.scan(
            TableName=table_name,
            ProjectionExpression="pk,sk",
            **start_key_kwargs,
        )
        yield from response["Items"]
        try:
            start_key_kwargs = {"ExclusiveStartKey": response["LastEvaluatedKey"]}
        except KeyError:
            break


def clear_dynamodb_table(
    client: DynamoDBClient, table_name: str, chunk_size=CHUNK_SIZE
):
    transact_items = []
    for item in _scan(client=client, table_name=table_name):
        transact_items.append({"Delete": {"TableName": table_name, "Key": item}})
        if len(transact_items) == chunk_size:
            client.transact_write_items(TransactItems=transact_items)
            transact_items = []
    if transact_items:
        client.transact_write_items(TransactItems=transact_items)


@contextmanager
def patch_dynamodb_client(client: DynamoDBClient):
    """
    Patch dynamodb 'query' operations that hit just a 'pk' because moto
    has a bug that doesn't return all results if there are multiple matches
    to the pk (i.e. with different values 'sk'). The alternative for
    testing purposes is to patch the 'query' into a 'scan' with filter
    """
    bare_query = client.query

    def _mocked_query(TableName, KeyConditionExpression=None, **kwargs):
        operation = bare_query
        if KeyConditionExpression == "pk = :pk":
            operation = client.scan
            kwargs["FilterExpression"] = KeyConditionExpression
        elif KeyConditionExpression:
            kwargs["KeyConditionExpression"] = KeyConditionExpression
        return operation(TableName=TableName, **kwargs)

    client.query = _mocked_query
    yield
    client.query = bare_query


@contextmanager
def mock_table_cpm(table_name: str):
    with mock_aws():
        client = dynamodb_client()
        with patch_dynamodb_client(client=client):
            client.create_table(
                TableName=table_name,
                AttributeDefinitions=ATTRIBUTE_DEFINITIONS_CPM,
                KeySchema=KEY_SCHEMAS,
                GlobalSecondaryIndexes=GLOBAL_SECONDARY_INDEXES_CPM,
                BillingMode="PAY_PER_REQUEST",
            )
            yield client
            client.delete_table(TableName=table_name)
