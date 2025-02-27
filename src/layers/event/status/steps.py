from http import HTTPStatus

from .errors import StatusNotOk


def _status_check(client, table_name: str) -> tuple[HTTPStatus, dict]:
    try:
        client.query(
            TableName=table_name,
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": {"S": "#NONE#"}},
        )
    except Exception as exception:
        raise StatusNotOk(exception)
    return HTTPStatus.OK, dict(code="OK", message="Transaction successful")


def status_check(data, cache) -> HTTPStatus:
    return _status_check(
        client=cache["DYNAMODB_CLIENT"], table_name=cache["DYNAMODB_TABLE"]
    )


steps = [
    status_check,
]
