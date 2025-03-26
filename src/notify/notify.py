import requests
from event.environment import BaseEnvironment


class NotifyEnvironment(BaseEnvironment):
    ENVIRONMENT: str
    SLACK_WEBHOOK_URL: str


ENVIRONMENT = NotifyEnvironment.build()


def send_notification(slack_webhook_url, **data):
    response = requests.post(url=slack_webhook_url, json=data)
    return response.text


def lambda_handler(event, context):
    data = event["Records"]
    subject_for_slack = data[0]["Sns"]["Subject"]
    message_for_slack = data[0]["Sns"]["Message"]
    state_for_slack = data[0]["Sns"]["MessageAttributes"]["State"]["Value"]

    response = send_notification(
        slack_webhook_url=ENVIRONMENT.SLACK_WEBHOOK_URL,
        environment=ENVIRONMENT.ENVIRONMENT,
        subject=subject_for_slack,
        message=message_for_slack,
        state=state_for_slack,
    )
    return {"statusCode": 200, "body": response}
