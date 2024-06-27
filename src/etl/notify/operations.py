from enum import StrEnum, auto

import requests
from etl_utils.trigger.model import TriggerResponse
from etl_utils.worker.model import WorkerResponse


class EtlStatus(StrEnum):
    PASS = auto()
    FAIL = auto()

    @classmethod
    def parse_response(cls, response: TriggerResponse):
        return cls.PASS if response.error_message is None else cls.FAIL


def parse_message(message: dict) -> TriggerResponse:
    try:
        return TriggerResponse(**message)
    except TypeError:
        pass

    try:
        response = WorkerResponse(**message)
        return TriggerResponse(
            message=(
                f"ETL stage '{response.stage_name}' generated {response.processed_records} "
                f"output records with {response.unprocessed_records} input records "
                "remaining to be processed"
            ),
            error_message=response.error_message,
        )
    except TypeError:
        pass

    return None


def send_notification(slack_webhook_url, **data):
    response = requests.post(url=slack_webhook_url, json=data)
    return response.text
