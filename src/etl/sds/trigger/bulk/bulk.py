import boto3
from aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType, TriggerEnvironment
from etl_utils.trigger.notify import notify
from event.aws.client import dynamodb_client
from event.step_chain import StepChain

from .steps import steps

S3_CLIENT = boto3.client("s3")
DYNAMODB_CLIENT = dynamodb_client()
STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")
LAMBDA_CLIENT = boto3.client("lambda")
ENVIRONMENT = TriggerEnvironment.build()

CACHE = {
    "s3_client": S3_CLIENT,
    "dynamodb_client": DYNAMODB_CLIENT,
    "step_functions_client": STEP_FUNCTIONS_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "table_name": ENVIRONMENT.TABLE_NAME,
}


@event_source(data_class=S3Event)
def handler(event: S3Event, context):
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(init=(event.bucket_name, event.object_key), cache=CACHE)
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=StateMachineInputType.BULK,
    )
