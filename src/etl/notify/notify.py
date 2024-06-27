from event.environment import BaseEnvironment

from etl.notify.operations import EtlStatus, parse_message, send_notification


class NotifyEnvironment(BaseEnvironment):
    WORKSPACE: str
    ENVIRONMENT: str
    SLACK_WEBHOOK_URL: str


ENVIRONMENT = NotifyEnvironment.build()


def handler(event: list[dict], context=None):
    status = EtlStatus.PASS
    for response in filter(bool, map(parse_message, event)):
        _status = EtlStatus.parse_response(response)
        send_notification(
            slack_webhook_url=ENVIRONMENT.SLACK_WEBHOOK_URL,
            workspace=ENVIRONMENT.WORKSPACE,
            environment=ENVIRONMENT.ENVIRONMENT,
            headline=response.message,
            error_message=response.error_message or "None",
        )
        if status is EtlStatus.PASS:
            status = _status

    return str(status)
