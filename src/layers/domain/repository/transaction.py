from contextlib import contextmanager
from enum import StrEnum
from typing import Literal, Optional

from botocore.exceptions import ClientError
from domain.core.error import NotFoundError
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
    ExpressionAttributeNames: Optional[dict] = Field(default=None)
    ExpressionAttributeValues: Optional[dict] = Field(default=None)


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
            statement = command.Put or command.Delete
            error = TRANSACTION_ERROR_MAPPING.get(statement.ConditionExpression)
            if error:
                raise error()
        raise UnhandledTransaction(
            message=response.Error.Message,
            code=response.Error.Code,
            unhandled_transactions=commands,
        )
