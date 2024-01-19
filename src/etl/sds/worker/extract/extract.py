from dataclasses import asdict

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.worker import WorkerEnvironment, WorkerResponse

CLIENT = boto3.client("s3")
ENVIRONMENT = WorkerEnvironment.build()


def handler(event, context):
    CLIENT.get_object(Bucket=ENVIRONMENT.ETL_BUCKET, Key=WorkerKey.EXTRACT)
    CLIENT.put_object(Bucket=ENVIRONMENT.ETL_BUCKET, Key=WorkerKey.TRANSFORM)
    response = WorkerResponse(
        stage_name="extract",
        count_processed=0,
        count_unprocessed=0,
        error_message=None,
    )
    return asdict(response)
