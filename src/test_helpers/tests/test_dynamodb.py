from domain.repository.marshall import marshall, marshall_value
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table_cpm, patch_dynamodb_client


def test_patch_dynamodb_client_patches_the_client():
    client = dynamodb_client()
    original_query_name = client.query.__name__
    with patch_dynamodb_client(client=client):
        # Test query is patched
        assert client.query.__name__ != original_query_name


def test_mock_table_query_pk():
    table_name = "my_table"
    pk = "common_key"
    sks = ["first", "second"]
    items = [marshall(pk=pk, sk=sk) for sk in sks]
    with mock_table_cpm(table_name) as client:
        for item in items:
            client.put_item(
                Item=item, ReturnConsumedCapacity="TOTAL", TableName=table_name
            )
        response = client.query(
            TableName=table_name,
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": marshall_value(pk)},
        )
    assert response["Items"] == items
