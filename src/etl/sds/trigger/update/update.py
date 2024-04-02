import boto3
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType, TriggerEnvironment
from etl_utils.trigger.notify import notify
from event.step_chain import StepChain

from .steps import steps

S3_CLIENT = boto3.client("s3")
STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")
LAMBDA_CLIENT = boto3.client("lambda")
ENVIRONMENT = TriggerEnvironment.build()

CACHE = {
    "s3_client": S3_CLIENT,
    "step_functions_client": STEP_FUNCTIONS_CLIENT,
    "state_machine_arn": ENVIRONMENT.STATE_MACHINE_ARN,
    "table_name": ENVIRONMENT.TABLE_NAME,
    "ldap_connection": None,
}


def handler(event={}, context=None):
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(cache=CACHE)
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=StateMachineInputType.UPDATE,
    )
