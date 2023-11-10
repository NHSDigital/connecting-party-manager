from typing import Generator

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
