from contextlib import contextmanager
from typing import Generator

from event.aws.client import dynamodb_client
from moto import mock_dynamodb

CHUNK_SIZE = 25

KEY_SCHEMAS = [
    {"AttributeName": "pk", "KeyType": "HASH"},
    {"AttributeName": "sk", "KeyType": "HASH"},
]
GLOBAL_SECONDARY_INDEXES = [
    {
        "IndexName": f"idx_gsi_{i}",
        "KeySchema": [
            {"AttributeName": f"pk_{i}", "KeyType": "HASH"},
            {"AttributeName": f"sk_{i}", "KeyType": "RANGE"},
        ],
        "Projection": {"ProjectionType": "ALL"},
    }
    for i in range(5)
]
ATTRIBUTE_DEFINITIONS = (
    [
        {"AttributeName": "pk", "AttributeType": "S"},
        {"AttributeName": "sk", "AttributeType": "S"},
    ]
    + [{"AttributeName": f"pk_{i}", "AttributeType": "S"} for i in range(5)]
    + [{"AttributeName": f"sk_{i}", "AttributeType": "S"} for i in range(5)]
)


def _chunk_list(list_a, chunk_size=CHUNK_SIZE):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i : i + chunk_size]


def _scan(client, table_name: str) -> Generator[dict, None, None]:
    start_key_kwargs = {}

    while True:
        response = client.scan(TableName=table_name, **start_key_kwargs)
        yield from response["Items"]
        try:
            start_key_kwargs = {"ExclusiveStartKey": response["LastEvaluatedKey"]}
        except KeyError:
            break


def clear_dynamodb_table(client, table_name: str):
    transact_items = [
        {
            "Delete": {
                "TableName": table_name,
                "Key": {"pk": item["pk"], "sk": item["sk"]},
            }
        }
        for item in _scan(client=client, table_name=table_name)
    ]
    for chunk in _chunk_list(transact_items):
        client.transact_write_items(TransactItems=chunk)


@contextmanager
def patch_dynamodb_client():
    """
    Patch dynamodb 'query' operations that hit just a 'pk' because moto
    has a bug that doesn't return all results if there are multiple matches
    to the pk (i.e. with different values 'sk'). The alternative for
    testing purposes is to patch the 'query' into a 'scan' with filter
    """
    client = dynamodb_client()
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
    yield client
    client.query = bare_query


@contextmanager
def mock_table(table_name: str):
    with mock_dynamodb():
        with patch_dynamodb_client() as client:
            client.create_table(
                TableName=table_name,
                AttributeDefinitions=ATTRIBUTE_DEFINITIONS,
                KeySchema=KEY_SCHEMAS,
                GlobalSecondaryIndexes=GLOBAL_SECONDARY_INDEXES,
                BillingMode="PAY_PER_REQUEST",
            )
            yield client
