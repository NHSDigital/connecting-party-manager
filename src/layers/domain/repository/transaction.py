from contextlib import contextmanager
from enum import StrEnum
from functools import partial
from typing import Literal, Optional

from botocore.exceptions import ClientError
from domain.core.error import NotFoundError
from domain.repository.marshall import marshall_value
from pydantic import BaseModel, Field

from .errors import AlreadyExistsError, UnhandledTransaction

ATTRIBUTE_NOT_EXISTS = "attribute_not_exists({})".format


class ConditionExpression(StrEnum):
    MUST_EXIST = "attribute_exists(pk) and attribute_exists(sk)"
    MUST_NOT_EXIST = " AND ".join(
        map(ATTRIBUTE_NOT_EXISTS, ("pk", "sk", "pk_1", "sk_1", "pk_2", "sk_2"))
    )


TRANSACTION_ERROR_MAPPING = {
    ConditionExpression.MUST_NOT_EXIST: AlreadyExistsError,
    ConditionExpression.MUST_EXIST: NotFoundError,
}


class TransactionStatement(BaseModel):
    TableName: str
    Item: Optional[dict] = Field(default=None)
    Key: Optional[dict] = Field(default=None)
    ConditionExpression: Optional["ConditionExpression"] = Field(default=None)
    UpdateExpression: Optional[str] = Field(default=None)
    ExpressionAttributeNames: Optional[dict]
    ExpressionAttributeValues: Optional[dict]


class TransactItem(BaseModel):
    Put: Optional[TransactionStatement] = None
    Delete: Optional[TransactionStatement] = None
    Update: Optional[TransactionStatement] = None


class Transaction(BaseModel):
    TransactItems: list[TransactItem]
    ReturnConsumedCapacity: Literal["NONE"] = "NONE"
    ReturnItemCollectionMetrics: Literal["NONE"] = "NONE"


class CancellationReason(BaseModel):
    Code: str

    @property
    def condition_check_failed(self) -> bool:
        return self.Code == "ConditionalCheckFailed"


class TransactionErrorMetadata(BaseModel):
    Message: str
    Code: str


class TransactionErrorResponse(BaseModel):
    Error: TransactionErrorMetadata
    CancellationReasons: list[CancellationReason] = Field(default_factory=list)

    def dict(self, *args, **kwargs):
        kwargs["exclude_none"] = True
        return super().dict(*args, **kwargs)


@contextmanager
def handle_client_errors(commands: list[TransactItem]):
    try:
        yield
    except ClientError as exc:
        response = TransactionErrorResponse(**exc.response)
        for reason, command in zip(response.CancellationReasons, commands):
            if not reason.condition_check_failed:
                continue
            statement = command.Put or command.Delete or command.Update
            error = TRANSACTION_ERROR_MAPPING.get(statement.ConditionExpression)
            if error:
                raise error()
        raise UnhandledTransaction(
            message=response.Error.Message,
            code=response.Error.Code,
            unhandled_transactions=commands,
        )


def _update_expression(updated_fields: dict) -> dict:
    expression_attribute_names = {}
    expression_attribute_values = {}
    update_clauses = []

    for field_name, value in updated_fields.items():
        field_name_placeholder = f"#{field_name}"
        field_value_placeholder = f":{field_name}"

        update_clauses.append(f"{field_name_placeholder} = {field_value_placeholder}")
        expression_attribute_names[field_name_placeholder] = field_name
        expression_attribute_values[field_value_placeholder] = marshall_value(value)

    update_expression = "SET " + ", ".join(update_clauses)

    return dict(
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )


def update_transactions(
    table_name: str, primary_keys: list[dict], data: dict
) -> list[TransactItem]:
    update_expression = _update_expression(updated_fields=data)
    update_statement = partial(
        TransactionStatement,
        TableName=table_name,
        ConditionExpression=ConditionExpression.MUST_EXIST,
        **update_expression,
    )
    transact_items = [
        TransactItem(Update=update_statement(Key=key)) for key in primary_keys
    ]
    return transact_items
