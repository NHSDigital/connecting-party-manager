import pytest
from botocore.exceptions import ClientError
from domain.repository.errors import AlreadyExistsError, UnhandledTransaction
from domain.repository.transaction import (
    CancellationReason,
    TransactionErrorMetadata,
    TransactionErrorResponse,
    TransactionItem,
    TransactionStatement,
    handle_client_errors,
)

COMMANDS = [
    TransactionItem(
        Put=TransactionStatement(
            TableName="table",
            Item={},
            ConditionExpression=(
                "attribute_not_exists(pk) AND attribute_not_exists(sk) "
                "AND attribute_not_exists(pk_1) AND attribute_not_exists(sk_1) "
                "AND attribute_not_exists(pk_2) AND attribute_not_exists(sk_2)"
            ),
        )
    )
]


@pytest.mark.parametrize(
    ["error_response", "exception"],
    [
        (
            TransactionErrorResponse(
                Error=TransactionErrorMetadata(
                    Message="oops",
                    Code="oops123",
                ),
                CancellationReasons=[],
            ),
            UnhandledTransaction(
                message="oops", code="oops123", unhandled_transactions=COMMANDS
            ),
        ),
        (
            TransactionErrorResponse(
                Error=TransactionErrorMetadata(
                    Message="oops",
                    Code="oops123",
                ),
                CancellationReasons=[CancellationReason(Code="woopsy")],
            ),
            UnhandledTransaction(
                message="oops", code="oops123", unhandled_transactions=COMMANDS
            ),
        ),
        (
            TransactionErrorResponse(
                Error=TransactionErrorMetadata(
                    Message="oops",
                    Code="oops123",
                ),
                CancellationReasons=[CancellationReason(Code="ConditionalCheckFailed")],
            ),
            AlreadyExistsError(),
        ),
    ],
)
def test_handle_client_errors(error_response: TransactionErrorResponse, exception):
    with pytest.raises(type(exception)) as exc:
        with handle_client_errors(commands=COMMANDS):
            raise ClientError(
                error_response=error_response.dict(), operation_name="PUT"
            )
    assert str(exc.value) == str(exception)


def test_handle_client_errors_does_not_fail():
    with handle_client_errors(commands=None):
        pass
    # implicit that no error has been raised
