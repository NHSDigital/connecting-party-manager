import os
from unittest import mock

EXAMPLE_DOT_COM = "https://httpbin.org"
NOTIFY_ENVIRONMENT = {
    "SLACK_WEBHOOK_URL": EXAMPLE_DOT_COM,
    "ENVIRONMENT": "foo",
}


example_sns_event = {
    "Records": [
        {
            "Sns": {
                "Subject": "Test Subject",
                "Message": "Test Message",
                "MessageAttributes": {"State": {"Value": "Test State"}},
            }
        }
    ]
}


def test_notify_lambda(input=example_sns_event):
    with mock.patch.dict(os.environ, NOTIFY_ENVIRONMENT, clear=True):
        from notify import notify

    result = notify.lambda_handler(event=input)
    assert result["statusCode"] == 200
