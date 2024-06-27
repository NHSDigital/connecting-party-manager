import pytest
from etl_utils.trigger.model import TriggerResponse

from etl.notify.operations import EtlStatus, parse_message, send_notification

from .test_notify_lambda import EXAMPLE_DOT_COM


@pytest.mark.parametrize(
    ["error_message", "status"],
    [
        (None, EtlStatus.PASS),
        ("oops", EtlStatus.FAIL),
    ],
)
def test_parse_response(error_message, status):
    assert (
        EtlStatus.parse_response(
            TriggerResponse(message="", error_message=error_message)
        )
        is status
    )


@pytest.mark.parametrize(
    ["message", "result"],
    [
        (
            {"message": "i'm a trigger response", "error_message": "oops"},
            TriggerResponse(message="i'm a trigger response", error_message="oops"),
        ),
        (
            {
                "stage_name": "bulk",
                "processed_records": 123,
                "unprocessed_records": 321,
                "error_message": "whoops",
            },
            TriggerResponse(
                message=(
                    "ETL stage 'bulk' generated 123 output records with "
                    "321 input records remaining to be processed"
                ),
                error_message="whoops",
            ),
        ),
        ({"foo": "bar"}, None),
    ],
)
def test_parse_message(message, result):
    assert parse_message(message=message) == result


def test_send_notification():
    response = send_notification(EXAMPLE_DOT_COM, foo=[123], bar="abc")
    assert len(response) > 0
