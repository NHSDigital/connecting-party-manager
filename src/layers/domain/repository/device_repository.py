from collections import defaultdict
from typing import TYPE_CHECKING

import orjson
from attr import asdict as _asdict
from domain.core.device import (
    Device,
    DeviceCreatedEvent,
    DeviceIndexAddedEvent,
    DeviceKey,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceType,
    DeviceUpdatedEvent,
)
from domain.core.load_questionnaire import render_question
from domain.core.questionnaire import (
    Questionnaire,
    QuestionnaireInstanceEvent,
    QuestionnaireResponse,
    QuestionnaireResponseAddedEvent,
    QuestionnaireResponseDeletedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from event.json import json_loads

from .errors import ItemNotFound
from .keys import TableKeys, strip_key_prefix
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository
from .transaction import ConditionExpression, TransactionStatement, TransactItem

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import QueryOutputTypeDef


def asdict(obj) -> dict:
    return _asdict(obj, recurse=False)


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def handle_DeviceCreatedEvent(
        self,
        event: DeviceCreatedEvent,
        condition_expression=ConditionExpression.MUST_NOT_EXIST,
    ) -> TransactItem:
        pk = TableKeys.DEVICE.key(event.id)
        pk_1 = TableKeys.DEVICE_TYPE.key(event.device_type)
        event_data = asdict(event)
        _condition_expression = (
            {"ConditionExpression": condition_expression}
            if event_data.get("_trust", False) is False
            else {}
        )
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=pk, pk_1=pk_1, sk_1=pk, **event_data),
                **_condition_expression,
            )
        )

    def handle_DeviceUpdatedEvent(self, event: DeviceUpdatedEvent) -> TransactItem:
        return self.handle_DeviceCreatedEvent(
            event=event, condition_expression=ConditionExpression.MUST_EXIST
        )

    def handle_DeviceKeyAddedEvent(self, event: DeviceKeyAddedEvent):
        pk = TableKeys.DEVICE.key(event.id)
        sk = TableKeys.DEVICE_KEY.key(event.key)
        pk_2 = TableKeys.DEVICE_KEY_TYPE.key(event.key_type)
        event_data = asdict(event)
        condition_expression = (
            {"ConditionExpression": ConditionExpression.MUST_NOT_EXIST}
            if event_data.get("_trust", False) is False
            else {}
        )
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=pk, sk=sk, pk_1=sk, sk_1=sk, pk_2=pk_2, sk_2=sk, **event_data
                ),
                **condition_expression,
            )
        )

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> TransactItem:
        pk = TableKeys.DEVICE.key(event.id)
        sk = TableKeys.DEVICE_KEY.key(event.key)
        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(pk=pk, sk=sk),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

    def handle_QuestionnaireInstanceEvent(self, event: QuestionnaireInstanceEvent):
        pk = TableKeys.DEVICE.key(event.entity_id)
        sk = TableKeys.QUESTIONNAIRE.key(event.questionnaire_id)
        event_data = asdict(event)
        event_data["questions"] = orjson.dumps(event_data["questions"]).decode()
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **event_data),
            )
        )

    def handle_QuestionnaireResponseAddedEvent(
        self,
        event: QuestionnaireResponseAddedEvent,
        condition_expression=ConditionExpression.MUST_NOT_EXIST,
    ) -> TransactItem:
        pk = TableKeys.DEVICE.key(event.entity_id)
        sk = TableKeys.QUESTIONNAIRE_RESPONSE.key(
            event.questionnaire_id, event.questionnaire_response_index
        )
        event_data = asdict(event)
        event_data["responses"] = orjson.dumps(event_data["responses"]).decode()
        condition_expression = (
            {"ConditionExpression": condition_expression}
            if event_data.get("_trust", False) is False
            else {}
        )
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **event_data),
                **condition_expression,
            )
        )

    def handle_QuestionnaireResponseUpdatedEvent(
        self, event: QuestionnaireResponseUpdatedEvent
    ) -> TransactItem:
        return self.handle_QuestionnaireResponseAddedEvent(
            event=event, condition_expression=ConditionExpression.MUST_EXIST
        )

    def handle_QuestionnaireResponseDeletedEvent(
        self, event: QuestionnaireResponseDeletedEvent
    ) -> TransactItem:
        pk = TableKeys.DEVICE.key(event.entity_id)
        sk = TableKeys.QUESTIONNAIRE_RESPONSE.key(
            event.questionnaire_id, event.questionnaire_response_index
        )
        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(pk=pk, sk=sk),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

    def handle_DeviceIndexAddedEvent(self, event: DeviceIndexAddedEvent):
        pk = TableKeys.DEVICE.key(event.id)
        sk = TableKeys.DEVICE_INDEX.key(
            event.questionnaire_id, event.question_name, event.value
        )
        event_data = asdict(event)
        condition_expression = (
            {"ConditionExpression": ConditionExpression.MUST_NOT_EXIST}
            if event_data.get("_trust", False) is False
            else {}
        )
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **asdict(event)),
                **condition_expression,
            )
        )

    def query_by_key_type(self, key_type, **kwargs) -> "QueryOutputTypeDef":
        pk_2 = TableKeys.DEVICE_KEY_TYPE.key(key_type)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_2",
            "KeyConditionExpression": "pk_2 = :pk_2",
            "ExpressionAttributeValues": {":pk_2": marshall_value(pk_2)},
        }
        return self.client.query(**args, **kwargs)

    def query_by_device_type(
        self, device_type: DeviceType, **kwargs
    ) -> "QueryOutputTypeDef":
        pk_1 = TableKeys.DEVICE_TYPE.key(device_type)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1",
            "ExpressionAttributeValues": {
                ":pk_1": marshall_value(pk_1),
            },
        }
        return self.client.query(**args, **kwargs)

    def read_by_index(self, questionnaire_id: str, question_name: str, value: str):
        pk_1 = TableKeys.DEVICE_INDEX.key(questionnaire_id, question_name, value)
        result = self.client.query(
            TableName=self.table_name,
            IndexName="idx_gsi_1",
            KeyConditionExpression="pk_1 = :pk_1",
            ExpressionAttributeValues={
                ":pk_1": marshall_value(pk_1),
            },
        )
        items = (unmarshall(i) for i in result["Items"])
        return [self.read(strip_key_prefix(item["pk"])) for item in items]

    def read_by_key(self, key) -> Device:
        pk_1 = TableKeys.DEVICE_KEY.key(key)
        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_1",
            "KeyConditionExpression": "pk_1 = :pk_1 AND sk_1 = :pk_1",
            "ExpressionAttributeValues": {":pk_1": marshall_value(pk_1)},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(key)
        (item,) = items
        return self.read(strip_key_prefix(item["pk"]))

    def read(self, id) -> Device:
        pk = TableKeys.DEVICE.key(id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": marshall_value(pk)},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(id)

        (device,) = TableKeys.DEVICE.filter(items, key="sk")
        keys = TableKeys.DEVICE_KEY.filter_and_group(items, key="sk")
        _indexes = TableKeys.DEVICE_INDEX.filter(items, key="sk")
        indexes = set(
            (idx["questionnaire_id"], idx["question_name"], idx["value"])
            for idx in _indexes
        )

        questionnaires = {}
        for id_, data in TableKeys.QUESTIONNAIRE.filter_and_group(items, key="sk"):
            data["questions"] = {
                question_name: render_question(question)
                for question_name, question in json_loads(data["questions"]).items()
            }
            questionnaires[id_] = Questionnaire(**data)

        questionnaire_responses = defaultdict(list)
        for qr in TableKeys.QUESTIONNAIRE_RESPONSE.filter(items, key="sk"):
            qid = qr["questionnaire_id"]
            _questionnaire_response = QuestionnaireResponse(
                questionnaire=questionnaires[qid], responses=json_loads(qr["responses"])
            )
            questionnaire_responses[qid].append(_questionnaire_response)

        return Device(
            keys={id_: DeviceKey(**data) for id_, data in keys},
            questionnaire_responses=questionnaire_responses,
            indexes=indexes,
            **device,
        )
