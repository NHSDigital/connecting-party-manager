# from collections import defaultdict
from copy import deepcopy
from typing import List

# import orjson
from attr import asdict as _asdict
from domain.core.device import (
    Device,
    DeviceCreatedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceUpdatedEvent,
)
from domain.core.error import NotFoundError

from .errors import ItemNotFound
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository
from .transaction import ConditionExpression, TransactionStatement, TransactItem

# from domain.core.load_questionnaire import render_question
# from domain.core.questionnaire import (
#     Questionnaire,
#     QuestionnaireInstanceEvent,
#     QuestionnaireResponse,
#     QuestionnaireResponseAddedEvent,
#     QuestionnaireResponseDeletedEvent,
#     QuestionnaireResponseUpdatedEvent,
# )
# from event.json import json_loads


# if TYPE_CHECKING:
#     from mypy_boto3_dynamodb.type_defs import QueryOutputTypeDef


def asdict(obj) -> dict:
    return _asdict(obj, recurse=False)


def _generate_update_expression(updates: dict):
    update_expression = "SET "
    expression_attribute_names = {}
    expression_attribute_values = {}

    update_clauses = []
    for key, value in updates.items():
        attribute_name_placeholder = f"#{key}"
        attribute_value_placeholder = f":{key}"

        update_clauses.append(
            f"{attribute_name_placeholder} = {attribute_value_placeholder}"
        )
        expression_attribute_names[attribute_name_placeholder] = key
        expression_attribute_values[attribute_value_placeholder] = marshall_value(value)

    update_expression += ", ".join(update_clauses)

    return update_expression, expression_attribute_names, expression_attribute_values


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def _batch_get_items(self, keys, id):
        list_of_keys = [{"pk": id, "sk": id}]
        for key in keys:
            list_of_keys.append({"pk": key, "sk": key})
            list_of_keys.append({"pk": id, "sk": key})

        request_items = {
            self.table_name: {
                "Keys": [
                    marshall(**key_to_marshall) for key_to_marshall in list_of_keys
                ]
            }
        }
        responses = self.client.batch_get_item(RequestItems=request_items)
        all_devices = responses.get("Responses", {}).get(self.table_name, [])

        yield from map(unmarshall, all_devices)

    def _update_all_devices_by_id_and_key(
        self, id, keys, updated_fields: dict
    ) -> List[TransactItem]:
        # Read all items by device ID
        all_devices_to_update = self._batch_get_items(keys=keys, id=id)

        transact_items = []
        (
            update_expression,
            expression_attribute_names,
            expression_attribute_values,
        ) = _generate_update_expression(updates=updated_fields)
        for device in all_devices_to_update:
            transact_item = TransactItem(
                Update=TransactionStatement(
                    TableName=self.table_name,
                    Key={
                        "pk": marshall_value(device["pk"]),
                        "sk": marshall_value(device["sk"]),
                    },
                    # need to produce a dict of keys and values
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    condition_expression=ConditionExpression.MUST_EXIST,
                )
            )
            transact_items.append(transact_item)

        return transact_items

    def _get_existing_keys_and_update_device_with_new_key(
        self, event: DeviceKeyAddedEvent, device_id, new_device_key
    ):
        device_by_id = self.read(id_or_key=device_id).dict()
        existing_device_keys = deepcopy(device_by_id.get("keys", {}))

        #  Make a copy of the device to avoid side effects and update keys
        updated_device = deepcopy(device_by_id)
        updated_device_keys = updated_device.get("keys", {})
        updated_device_keys[new_device_key] = event.key_type
        updated_device["keys"] = updated_device_keys

        return existing_device_keys, updated_device

    def _get_existing_keys_and_remove_key_from_device(
        self, event: DeviceKeyDeletedEvent, device_id, device_key_to_delete
    ):
        device_by_id = self.read(id_or_key=device_id).dict()
        existing_device_keys = deepcopy(device_by_id.get("keys", {}))

        #  Make a copy of the device to avoid side effects and update keys
        updated_device = deepcopy(device_by_id)
        updated_device_keys = updated_device.get("keys", {})
        try:
            updated_device_keys.pop(device_key_to_delete)
        except KeyError:
            raise NotFoundError(
                f"This device does not contain key '{device_key_to_delete}'"
            ) from None

        updated_device["keys"] = updated_device_keys

        return existing_device_keys, updated_device

    def handle_DeviceCreatedEvent(
        self,
        event: DeviceCreatedEvent,
        condition_expression=ConditionExpression.MUST_NOT_EXIST,
    ) -> TransactItem:
        # Initial device is sorted by its own id
        pk = str(event.id)
        sk = str(event.id)

        event_data = asdict(event)
        _condition_expression = (
            {"ConditionExpression": condition_expression}
            if event_data.get("_trust", False) is False
            else {}
        )
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=pk, sk=sk, **event_data),
                **_condition_expression,
            )
        )

    def handle_DeviceUpdatedEvent(self, event: DeviceUpdatedEvent) -> TransactItem:
        # updating the existing device with the new event
        device_keys = event.keys
        device_id = event.id
        updated_device = asdict(event)

        transaction_items = self._update_all_devices_by_id_and_key(
            id=device_id,
            keys=device_keys,
            updated_fields=updated_device,
        )

        return transaction_items

    def handle_DeviceKeyAddedEvent(
        self, event: DeviceKeyAddedEvent
    ) -> List[TransactItem]:
        device_id = str(event.id)
        new_device_key = str(event.key)

        event_data = asdict(event)

        condition_expression = (
            {"ConditionExpression": ConditionExpression.MUST_NOT_EXIST}
            if event_data.get("_trust", False) is False
            else {}
        )

        #  Get a copy of the existing keys and update the device with new key
        (
            existing_device_keys,
            updated_device,
        ) = self._get_existing_keys_and_update_device_with_new_key(
            event, device_id, new_device_key
        )

        transaction_items = self._update_all_devices_by_id_and_key(
            id=device_id,
            keys=existing_device_keys,
            updated_fields={"keys": updated_device["keys"]},
        )

        create_device_by_id_and_key = TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=device_id, sk=new_device_key, **updated_device),
                **condition_expression,
            )
        )
        create_device_by_key = TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=new_device_key, sk=new_device_key, **updated_device),
                **condition_expression,
            )
        )
        transaction_items.append(create_device_by_id_and_key)
        transaction_items.append(create_device_by_key)
        return transaction_items

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> TransactItem:
        device_id = str(event.id)
        device_key_to_delete = str(event.key)

        (
            existing_device_keys,
            updated_device,
        ) = self._get_existing_keys_and_update_device_with_new_key(
            event, device_id, new_device_key
        )

        transaction_items = self._update_all_devices_by_id_and_key(
            id=device_id,
            keys=existing_device_keys,
            updated_device=updated_device,
        )

        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(pk=pk, sk=sk),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

    def read(self, id_or_key) -> Device:
        pk = str(id_or_key)
        sk = str(id_or_key)

        args = {"TableName": self.table_name, "Key": {"pk": {"S": pk}, "sk": {"S": sk}}}

        result = self.client.get_item(**args)
        item = result.get("Item")
        if not item:
            raise ItemNotFound(id)

        device = unmarshall(item)
        return Device(
            **device,
        )

    # def query_by_key_type(self, key_type, **kwargs) -> "QueryOutputTypeDef":
    #     pk_2 = TableKeys.DEVICE_KEY_TYPE.key(key_type)
    #     args = {
    #         "TableName": self.table_name,
    #         "IndexName": "idx_gsi_2",
    #         "KeyConditionExpression": "pk_2 = :pk_2",
    #         "ExpressionAttributeValues": {":pk_2": marshall_value(pk_2)},
    #     }
    #     results = self.client.query(**args, **kwargs)
    #     results = map(unmarshall, results["Items"])
    #     return device

    # def handle_QuestionnaireInstanceEvent(self, event: QuestionnaireInstanceEvent):
    #     pk = TableKeys.DEVICE.key(event.entity_id)
    #     sk = TableKeys.QUESTIONNAIRE.key(event.questionnaire_id)
    #     event_data = asdict(event)
    #     event_data["questions"] = orjson.dumps(event_data["questions"]).decode()
    #     return TransactItem(
    #         Put=TransactionStatement(
    #             TableName=self.table_name,
    #             Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **event_data),
    #         )
    #     )

    # def handle_QuestionnaireResponseAddedEvent(
    #     self,
    #     event: QuestionnaireResponseAddedEvent,
    #     condition_expression=ConditionExpression.MUST_NOT_EXIST,
    # ) -> TransactItem:
    #     pk = TableKeys.DEVICE.key(event.entity_id)
    #     sk = TableKeys.QUESTIONNAIRE_RESPONSE.key(
    #         event.questionnaire_id, event.questionnaire_response_index
    #     )
    #     event_data = asdict(event)
    #     event_data["responses"] = orjson.dumps(event_data["responses"]).decode()
    #     condition_expression = (
    #         {"ConditionExpression": condition_expression}
    #         if event_data.get("_trust", False) is False
    #         else {}
    #     )
    #     return TransactItem(
    #         Put=TransactionStatement(
    #             TableName=self.table_name,
    #             Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **event_data),
    #             **condition_expression,
    #         )
    #     )

    # def handle_QuestionnaireResponseUpdatedEvent(
    #     self, event: QuestionnaireResponseUpdatedEvent
    # ) -> TransactItem:
    #     return self.handle_QuestionnaireResponseAddedEvent(
    #         event=event, condition_expression=ConditionExpression.MUST_EXIST
    #     )

    # def handle_QuestionnaireResponseDeletedEvent(
    #     self, event: QuestionnaireResponseDeletedEvent
    # ) -> TransactItem:
    #     pk = TableKeys.DEVICE.key(event.entity_id)
    #     sk = TableKeys.QUESTIONNAIRE_RESPONSE.key(
    #         event.questionnaire_id, event.questionnaire_response_index
    #     )
    #     return TransactItem(
    #         Delete=TransactionStatement(
    #             TableName=self.table_name,
    #             Key=marshall(pk=pk, sk=sk),
    #             ConditionExpression=ConditionExpression.MUST_EXIST,
    #         )
    #     )

    # def handle_DeviceIndexAddedEvent(self, event: DeviceIndexAddedEvent):
    #     pk = TableKeys.DEVICE.key(event.id)
    #     sk = TableKeys.DEVICE_INDEX.key(
    #         event.questionnaire_id, event.question_name, event.value
    #     )
    #     event_data = asdict(event)
    #     condition_expression = (
    #         {"ConditionExpression": ConditionExpression.MUST_NOT_EXIST}
    #         if event_data.get("_trust", False) is False
    #         else {}
    #     )
    #     return TransactItem(
    #         Put=TransactionStatement(
    #             TableName=self.table_name,
    #             Item=marshall(pk=pk, sk=sk, pk_1=sk, sk_1=pk, **asdict(event)),
    #             **condition_expression,
    #         )
    #     )

    # def query_by_key_type(self, key_type, **kwargs) -> "QueryOutputTypeDef":
    #     pk_2 = TableKeys.DEVICE_KEY_TYPE.key(key_type)
    #     args = {
    #         "TableName": self.table_name,
    #         "IndexName": "idx_gsi_2",
    #         "KeyConditionExpression": "pk_2 = :pk_2",
    #         "ExpressionAttributeValues": {":pk_2": marshall_value(pk_2)},
    #     }
    #     return self.client.query(**args, **kwargs)

    # def query_by_device_type(self, type: DeviceType, **kwargs) -> "QueryOutputTypeDef":
    #     pk_1 = TableKeys.DEVICE_TYPE.key(type)
    #     args = {
    #         "TableName": self.table_name,
    #         "IndexName": "idx_gsi_1",
    #         "KeyConditionExpression": "pk_1 = :pk_1",
    #         "ExpressionAttributeValues": {
    #             ":pk_1": marshall_value(pk_1),
    #         },
    #     }
    #     return self.client.query(**args, **kwargs)

    # def read_by_index(self, questionnaire_id: str, question_name: str, value: str):
    #     pk_1 = TableKeys.DEVICE_INDEX.key(questionnaire_id, question_name, value)
    #     result = self.client.query(
    #         TableName=self.table_name,
    #         IndexName="idx_gsi_1",
    #         KeyConditionExpression="pk_1 = :pk_1",
    #         ExpressionAttributeValues={
    #             ":pk_1": marshall_value(pk_1),
    #         },
    #     )
    #     items = (unmarshall(i) for i in result["Items"])
    #     return [self.read(strip_key_prefix(item["pk"])) for item in items]

    # def read_by_key(self, key) -> Device:
    #     pk_1 = TableKeys.DEVICE_KEY.key(key)
    #     args = {
    #         "TableName": self.table_name,
    #         "IndexName": "idx_gsi_1",
    #         "KeyConditionExpression": "pk_1 = :pk_1 AND sk_1 = :pk_1",
    #         "ExpressionAttributeValues": {":pk_1": marshall_value(pk_1)},
    #     }
    #     result = self.client.query(**args)
    #     items = [unmarshall(i) for i in result["Items"]]
    #     if len(items) == 0:
    #         raise ItemNotFound(key)
    #     (item,) = items
    #     return self.read(strip_key_prefix(item["pk"]))

    # def read(self, id) -> Device:
    #     pk = TableKeys.DEVICE.key(id)
    #     args = {
    #         "TableName": self.table_name,
    #         "KeyConditionExpression": "pk = :pk",
    #         "ExpressionAttributeValues": {":pk": marshall_value(pk)},
    #     }
    #     result = self.client.query(**args)
    #     items = [unmarshall(i) for i in result["Items"]]
    #     if len(items) == 0:
    #         raise ItemNotFound(id)

    #     (device,) = TableKeys.DEVICE.filter(items, key="sk")
    #     keys = TableKeys.DEVICE_KEY.filter_and_group(items, key="sk")

    #     questionnaires = {}
    #     for id_, data in TableKeys.QUESTIONNAIRE.filter_and_group(items, key="sk"):
    #         data["questions"] = {
    #             question_name: render_question(question)
    #             for question_name, question in json_loads(data["questions"]).items()
    #         }
    #         questionnaires[id_] = Questionnaire(**data)

    #     questionnaire_responses = defaultdict(list)
    #     for qr in TableKeys.QUESTIONNAIRE_RESPONSE.filter(items, key="sk"):
    #         qid = qr["questionnaire_id"]
    #         _questionnaire_response = QuestionnaireResponse(
    #             questionnaire=questionnaires[qid], responses=json_loads(qr["responses"])
    #         )
    #         questionnaire_responses[qid].append(_questionnaire_response)

    #     return Device(
    #         keys={id_: DeviceKey(**data) for id_, data in keys},
    #         questionnaire_responses=questionnaire_responses,
    #         **device,
    #     )
