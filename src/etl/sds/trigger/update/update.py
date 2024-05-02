import base64
from pathlib import Path

import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType
from etl_utils.trigger.notify import notify
from event.environment import BaseEnvironment
from event.step_chain import StepChain

from .steps import steps


class ChangelogTriggerEnvironment(BaseEnvironment):
    STATE_MACHINE_ARN: str
    NOTIFY_LAMBDA_ARN: str
    TRUSTSTORE_BUCKET: str
    CPM_FQDN: str
    LDAP_HOST: str
    ETL_BUCKET: str
    LDAP_CHANGELOG_USER: str
    LDAP_CHANGELOG_PASSWORD: str


S3_CLIENT = boto3.client("s3")
STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")
LAMBDA_CLIENT = boto3.client("lambda")
ENVIRONMENT = ChangelogTriggerEnvironment.build()


CACHE = {
    "s3_client": S3_CLIENT,
    "step_functions_client": STEP_FUNCTIONS_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "truststore_bucket": ENVIRONMENT.TRUSTSTORE_BUCKET,
    "cert_file": Path(f"/tmp/{ENVIRONMENT.CPM_FQDN}.crt"),
    "key_file": Path(f"/tmp/{ENVIRONMENT.CPM_FQDN}.key"),
    "etl_bucket": ENVIRONMENT.ETL_BUCKET,
    "ldap_host": ENVIRONMENT.LDAP_HOST,
    "ldap_changelog_user": ENVIRONMENT.LDAP_CHANGELOG_USER,
    "ldap_changelog_password": str(
        base64.b64encode(ENVIRONMENT.LDAP_CHANGELOG_PASSWORD.encode("utf-8")).decode(
            "utf-8"
        )
    ),
}


def handler(event={}, context=None):
    if "ldap" not in CACHE:
        import ldap

        CACHE["ldap"] = ldap

    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(cache=CACHE)
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=StateMachineInputType.UPDATE,
    )
