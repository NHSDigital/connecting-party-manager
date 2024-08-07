import logging

import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType
from etl_utils.trigger.notify import notify
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.step_chain import StepChain

from .steps import _publish_message_to_sqs_queue, steps


class ExecutionRunningError(Exception):
    """Custom exception for existing ETL execution Running."""

    pass


class ManualTriggerEnvironment(BaseEnvironment):
    SQS_QUEUE_URL: str
    NOTIFY_LAMBDA_ARN: str
    ETL_BUCKET: str
    STATE_MACHINE_ARN: str


S3_CLIENT = boto3.client("s3")
LAMBDA_CLIENT = boto3.client("lambda")
SQS_CLIENT = boto3.client("sqs")
SF_CLIENT = boto3.client("stepfunctions")
ENVIRONMENT = ManualTriggerEnvironment.build()

CACHE = {
    "s3_client": S3_CLIENT,
    "etl_bucket": ENVIRONMENT.ETL_BUCKET,
    "sqs_client": SQS_CLIENT,
    "sqs_queue_url": ENVIRONMENT.SQS_QUEUE_URL,
    "sf_client": SF_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "manual_retry_state": True,
}


def handler(event, context):
    manual_retry = True
    setup_logger(service_name=__file__)
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    try:
        step_chain.run(
            init=(ENVIRONMENT.ETL_BUCKET, manual_retry, ENVIRONMENT.STATE_MACHINE_ARN),
            cache=CACHE,
        )
        trigger_type = "null"
        result = step_chain.data[_publish_message_to_sqs_queue]
        if result:
            if result.upper() == "BULK":
                trigger_type = StateMachineInputType.BULK
            if result.upper() == "UPDATE":
                trigger_type = StateMachineInputType.UPDATE
        else:
            raise ExecutionRunningError("An execution is Running.")

        return notify(
            lambda_client=LAMBDA_CLIENT,
            function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
            result=step_chain.result,
            trigger_type=trigger_type,
        )
    except ExecutionRunningError as e:
        logging.error(f"ExecutionRunningError: {e}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
