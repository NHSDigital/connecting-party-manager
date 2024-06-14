import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.notify import notify
from event.environment import BaseEnvironment
from event.step_chain import StepChain

from .steps import _process_sqs_message, steps


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
    "etl_bucket": ENVIRONMENT.ETL_BUCKET,
}


def handler(event=dict, context=None):
    for message in event["Records"]:
        process_message(message)

    return None  # Message removed from sqs queue


def process_message(message):
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(cache=CACHE, init=message)

    trigger_type = "null"
    result = step_chain.data[_process_sqs_message]

    if isinstance(result, tuple):
        state_machine_input, _ = result
        if not isinstance(state_machine_input, Exception):
            trigger_type = state_machine_input.etl_type
    else:
        # If the result is not a tuple, it must be an Exception
        state_machine_input = result

    response = notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=trigger_type,
    )

    return response
