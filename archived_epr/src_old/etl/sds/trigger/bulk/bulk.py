import boto3
from aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from etl_utils.trigger.logger import log_action
from etl_utils.trigger.model import StateMachineInputType
from etl_utils.trigger.notify import notify
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.step_chain import StepChain

from .steps import steps


class BulkTriggerEnvironment(BaseEnvironment):
    NOTIFY_LAMBDA_ARN: str
    TABLE_NAME: str
    SQS_QUEUE_URL: str


S3_CLIENT = boto3.client("s3")
DYNAMODB_CLIENT = dynamodb_client()
LAMBDA_CLIENT = boto3.client("lambda")
SQS_CLIENT = boto3.client("sqs")
ENVIRONMENT = BulkTriggerEnvironment.build()

CACHE = {
    "s3_client": S3_CLIENT,
    "dynamodb_client": DYNAMODB_CLIENT,
    "sqs_client": SQS_CLIENT,
    "table_name": ENVIRONMENT.TABLE_NAME,
    "sqs_queue_url": ENVIRONMENT.SQS_QUEUE_URL,
}


@event_source(data_class=S3Event)
def handler(event: S3Event, context):
    setup_logger(service_name=__file__)
    step_chain = StepChain(step_chain=steps, step_decorators=[log_action])
    step_chain.run(init=(event.bucket_name, event.object_key), cache=CACHE)
    return notify(
        lambda_client=LAMBDA_CLIENT,
        function_name=ENVIRONMENT.NOTIFY_LAMBDA_ARN,
        result=step_chain.result,
        trigger_type=StateMachineInputType.BULK,
    )
