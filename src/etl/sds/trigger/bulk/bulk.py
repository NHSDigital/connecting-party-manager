import boto3
from aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from etl_utils.trigger.model import StateMachineInput, TriggerEnvironment
from etl_utils.trigger.notify import notify
from event.aws.client import dynamodb_client
from event.step_chain import StepChain
from nhs_context_logging import log_action

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
    state_machine_input = StateMachineInput.bulk()
    step_chain = StepChain(
        step_chain=steps,
        step_decorators=[
            lambda fn: log_action(
                log_args=["data", "cache"],
                log_result=True,
            )(fn)
        ],
    )
    step_chain.run(
        init=(event.bucket_name, event.object_key, state_machine_input), cache=CACHE
    )
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        state_machine_name=state_machine_input.name,
    )
