from contextlib import contextmanager
from typing import Generator

import boto3
from moto import mock_dynamodb

CHUNK_SIZE = 25


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
def mock_table(table_name: str):
    key_schemas = [
        {"AttributeName": "pk", "KeyType": "HASH"},
        {"AttributeName": "sk", "KeyType": "HASH"},
    ]
    global_secondary_indexes = [
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
    attribute_definitions = (
        [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ]
        + [{"AttributeName": f"pk_{i}", "AttributeType": "S"} for i in range(5)]
        + [{"AttributeName": f"sk_{i}", "AttributeType": "S"} for i in range(5)]
    )

    with mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            TableName=table_name,
            AttributeDefinitions=attribute_definitions,
            KeySchema=key_schemas,
            GlobalSecondaryIndexes=global_secondary_indexes,
            BillingMode="PAY_PER_REQUEST",
        )
        yield client
