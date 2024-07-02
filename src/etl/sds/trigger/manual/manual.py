# import json

import boto3

# f  # rom aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType
from etl_utils.trigger.notify import notify
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.step_chain import StepChain

from .steps import steps


class ManualTriggerEnvironment(BaseEnvironment):
    STATE_MACHINE_ARN: str
    NOTIFY_LAMBDA_ARN: str
    TABLE_NAME: str


S3_CLIENT = boto3.client("s3")
DYNAMODB_CLIENT = dynamodb_client()
STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")
LAMBDA_CLIENT = boto3.client("lambda")
ENVIRONMENT = ManualTriggerEnvironment.build()

CACHE = {
    "s3_client": S3_CLIENT,
    "dynamodb_client": DYNAMODB_CLIENT,
    "step_functions_client": STEP_FUNCTIONS_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "table_name": ENVIRONMENT.TABLE_NAME,
}


# @event_source(data_class=S3Event)
def handler(event, context):
    # print("Received event:", json.dumps(event))
    setup_logger(service_name=__file__)
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(
        init=(
            event.get("bucket_name"),
            event.get("object_key"),
            event.get("manual_retry"),
            event.get("etl_type"),
        ),
        cache=CACHE,
    )
    if event.get("etl_type").upper() == "BULK":
        trigger_type = StateMachineInputType.BULK
    elif event.get("etl_type").upper() == "UPDATE":
        trigger_type = StateMachineInputType.UPDATE
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=trigger_type,
    )
