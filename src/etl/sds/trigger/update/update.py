from pathlib import Path

import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType
from etl_utils.trigger.notify import notify
from event.environment import BaseEnvironment
from event.logging.constants import LDAP_REDACTED_FIELDS
from event.logging.logger import setup_logger
from event.step_chain import StepChain

from .steps import steps


class ChangelogTriggerEnvironment(BaseEnvironment):
    NOTIFY_LAMBDA_ARN: str
    TRUSTSTORE_BUCKET: str
    CPM_FQDN: str
    LDAP_HOST: str
    ETL_BUCKET: str
    LDAP_CHANGELOG_USER: str
    LDAP_CHANGELOG_PASSWORD: str
    SQS_QUEUE_URL: str


S3_CLIENT = boto3.client("s3")
LAMBDA_CLIENT = boto3.client("lambda")
SQS_CLIENT = boto3.client("sqs")
ENVIRONMENT = ChangelogTriggerEnvironment.build()


CACHE = {
    "s3_client": S3_CLIENT,
    "sqs_client": SQS_CLIENT,
    "truststore_bucket": ENVIRONMENT.TRUSTSTORE_BUCKET,
    "cert_file": Path(f"/tmp/{ENVIRONMENT.CPM_FQDN}.crt"),
    "key_file": Path(f"/tmp/{ENVIRONMENT.CPM_FQDN}.key"),
    "etl_bucket": ENVIRONMENT.ETL_BUCKET,
    "ldap_host": ENVIRONMENT.LDAP_HOST,
    "ldap_changelog_user": ENVIRONMENT.LDAP_CHANGELOG_USER,
    "ldap_changelog_password": ENVIRONMENT.LDAP_CHANGELOG_PASSWORD,
    "sqs_queue_url": ENVIRONMENT.SQS_QUEUE_URL,
}


def handler(event={}, context=None):
    if "ldap" not in CACHE:
        import ldap

        CACHE["ldap"] = ldap

    setup_logger(service_name=__file__, redacted_fields=LDAP_REDACTED_FIELDS)

    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(cache=CACHE)
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=StateMachineInputType.UPDATE,
    )
