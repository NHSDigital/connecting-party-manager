import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.notify import notify
from event.environment import BaseEnvironment
from event.step_chain import StepChain

from .steps import _process_sqs_message, steps


class EtlStateLockEnvironment(BaseEnvironment):
    STATE_MACHINE_ARN: str
    NOTIFY_LAMBDA_ARN: str
    ETL_BUCKET: str


S3_CLIENT = boto3.client("s3")
STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")
LAMBDA_CLIENT = boto3.client("lambda")
ENVIRONMENT = EtlStateLockEnvironment.build()


CACHE = {
    "s3_client": S3_CLIENT,
    "step_functions_client": STEP_FUNCTIONS_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "etl_bucket": ENVIRONMENT.ETL_BUCKET,
    "manual_retry_state": False,
}


def handler(event=dict, context=None):
    for message in event["Records"]:
        process_message(message)

    return None  # Returning None is crucial because it indicates a successful processing of the message to the SQS service.
    # If this return value is changed, the SQS service might interpret it as a failure, causing the message to be retried or stuck in the queue.


def process_message(message):
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(cache=CACHE, init=message)

    trigger_type = "null"
    result = step_chain.data[_process_sqs_message]
    if isinstance(result, tuple):
        state_machine_input, _ = result
        if not isinstance(state_machine_input, Exception):
            trigger_type = state_machine_input.etl_type

    response = notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=trigger_type,
    )

    return response
