from contextlib import contextmanager
from enum import StrEnum
from typing import Literal

from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from .errors import AlreadyExistsError, UnhandledTransaction

ATTRIBUTE_NOT_EXISTS = "attribute_not_exists({})".format


class ConditionExpression(StrEnum):
    MUST_NOT_EXIST = " AND ".join(
        map(ATTRIBUTE_NOT_EXISTS, ("pk", "sk", "pk_1", "sk_1", "pk_2", "sk_2"))
    )


TRANSACTION_ERROR_MAPPING = {
    ConditionExpression.MUST_NOT_EXIST: AlreadyExistsError,
}


class TransactionStatement(BaseModel):
    TableName: str
    Item: dict
    ConditionExpression: "ConditionExpression" = Field(default=None)


class TransactionItem(BaseModel):
    Put: TransactionStatement


class Transaction(BaseModel):
    TransactItems: list[TransactionItem]
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
def handle_client_errors(commands: list[TransactionItem]):
    try:
        yield
    except ClientError as exc:
        response = TransactionErrorResponse(**exc.response)
        for reason, command in zip(response.CancellationReasons, commands):
            if not reason.condition_check_failed:
                continue
            error = TRANSACTION_ERROR_MAPPING.get(command.Put.ConditionExpression)
            if error:
                raise error()
        raise UnhandledTransaction(
            message=response.Error.Message,
            code=response.Error.Code,
            unhandled_transactions=commands,
        )
