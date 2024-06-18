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

# from domain.core.error import NotFoundError
# from domain.core.load_questionnaire import render_question
# from domain.core.questionnaire import (
#     Questionnaire,
#     QuestionnaireInstanceEvent,
#     QuestionnaireResponse,
#     QuestionnaireResponseAddedEvent,
#     QuestionnaireResponseDeletedEvent,
#     QuestionnaireResponseUpdatedEvent,
# )
from domain.core.device_key import DeviceKey
from domain.repository.keys import TableKeys

from .errors import ItemNotFound
from .marshall import marshall, marshall_value, unmarshall
from .repository import Repository
from .transaction import ConditionExpression, TransactionStatement, TransactItem

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

    def _batch_get_items(self, keys: list[DeviceKey], id):
        list_of_keys = []
        for device_key in keys:
            list_of_keys.append(
                {
                    "pk": TableKeys.DEVICE.key(device_key["key"]),
                    "sk": TableKeys.DEVICE.key(device_key["key"]),
                }
            )

        list_of_keys.append(
            {"pk": TableKeys.DEVICE.key(id), "sk": TableKeys.DEVICE.key(id)}
        )
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

    def _transact_items_to_update_all_devices_by_id_and_key(
        self, id: str, keys: list[DeviceKey], updated_fields: dict
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
        self, event: DeviceKeyAddedEvent
    ):
        device_by_id = self.read_by_id(id=event.id).dict()

        #  Make a copy of the device and keys to avoid side effects and update keys
        existing_device_keys = deepcopy(device_by_id.get("keys", {}))
        updated_device = deepcopy(device_by_id)

        updated_device_keys: list = updated_device.get("keys", {})
        device_key = DeviceKey(key=event.key, type=event.key_type).dict()

        updated_device_keys.append(device_key)

        updated_device["keys"] = updated_device_keys

        return existing_device_keys, updated_device

    def _get_existing_keys_and_remove_key_from_device(
        self, device_id, device_key_to_delete
    ):
        device_by_id = self.read_by_id(id=device_id).dict()

        #  Make a copy of the device to avoid side effects and update keys
        updated_device = deepcopy(device_by_id)
        updated_device_keys: dict = updated_device["keys"]
        updated_device_keys.pop(device_key_to_delete)
        updated_device["keys"] = updated_device_keys

        return updated_device

    def handle_DeviceCreatedEvent(
        self,
        event: DeviceCreatedEvent,
        condition_expression=ConditionExpression.MUST_NOT_EXIST,
    ) -> TransactItem:
        # Initial device is sorted by its own id
        device_id_pk = TableKeys.DEVICE.key(event.id)
        device_id_sk = TableKeys.DEVICE.key(event.id)

        event_data = asdict(event)
        _condition_expression = (
            {"ConditionExpression": condition_expression}
            if event_data.get("_trust", False) is False
            else {}
        )

        # Setting Root = True is how we deduplicate the records in Opensearch
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=device_id_pk, sk=device_id_sk, root=True, **event_data
                ),
                **_condition_expression,
            )
        )

    def handle_DeviceUpdatedEvent(self, event: DeviceUpdatedEvent) -> TransactItem:
        # updating the existing device with the new event
        device_keys = event.keys
        device_id = event.id
        updated_device = asdict(event)

        transaction_items = self._transact_items_to_update_all_devices_by_id_and_key(
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
        ) = self._get_existing_keys_and_update_device_with_new_key(event=event)

        transaction_items = self._transact_items_to_update_all_devices_by_id_and_key(
            id=device_id,
            keys=existing_device_keys,
            updated_fields={"keys": updated_device["keys"]},
        )

        create_device_by_key = TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=TableKeys.DEVICE.key(new_device_key),
                    sk=TableKeys.DEVICE.key(new_device_key),
                    **updated_device,
                ),
                **condition_expression,
            )
        )
        transaction_items.append(create_device_by_key)
        return transaction_items

    def handle_DeviceKeyDeletedEvent(
        self, event: DeviceKeyDeletedEvent
    ) -> TransactItem:
        device_id = str(event.id)
        device_key_to_delete = str(event.key)
        remaining_keys = event.remaining_keys

        updated_device = self._get_existing_keys_and_remove_key_from_device(
            device_id=device_id, device_key_to_delete=device_key_to_delete
        )

        transaction_items = self._transact_items_to_update_all_devices_by_id_and_key(
            id=device_id,
            keys=remaining_keys,
            updated_fields={"keys": updated_device["keys"]},
        )

        delete_device_by_id_and_key = TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(
                    pk=TableKeys.DEVICE.key(device_id),
                    sk=TableKeys.DEVICE.key(device_key_to_delete),
                ),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )
        delete_device_by_key = TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(
                    pk=TableKeys.DEVICE.key(device_key_to_delete),
                    sk=TableKeys.DEVICE.key(device_key_to_delete),
                ),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

        transaction_items.append(delete_device_by_id_and_key)
        transaction_items.append(delete_device_by_key)
        return transaction_items

    def read_by_id(self, id) -> Device:
        pk = TableKeys.DEVICE.key(id)
        sk = TableKeys.DEVICE.key(id)

        args = {"TableName": self.table_name, "Key": {"pk": {"S": pk}, "sk": {"S": sk}}}

        result = self.client.get_item(**args)
        item = result.get("Item")
        if not item:
            raise ItemNotFound(id)

        device = unmarshall(item)
        return Device(
            **device,
        )

    def read_by_key(self, key) -> Device:
        pk = TableKeys.DEVICE.key(key)
        sk = TableKeys.DEVICE.key(key)

        args = {"TableName": self.table_name, "Key": {"pk": {"S": pk}, "sk": {"S": sk}}}

        result = self.client.get_item(**args)
        item = result.get("Item")
        if not item:
            raise ItemNotFound(id)

        device = unmarshall(item)
        return Device(
            **device,
        )

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
    #     sk = TableKeys.DEVICE.key(
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
