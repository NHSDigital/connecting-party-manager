from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from domain.core.event_deserializer import deserialize_event
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from sds.epr.updates.etl_update_repository import EtlUpdateRepository
from sds.worker.load import LoadWorkerEnvironment

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

ENVIRONMENT = LoadWorkerEnvironment.build()


class LoadWorkerCache:
    def __init__(self):
        self.S3_CLIENT = boto3.client("s3")
        self.ENVIRONMENT = ENVIRONMENT
        self.REPOSITORY = EtlUpdateRepository(
            table_name=ENVIRONMENT.TABLE_NAME, dynamodb_client=dynamodb_client()
        )
        self.MAX_RECORDS = 150_000


CACHE = LoadWorkerCache()


def load(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    """
    For updates, the transformed data needs converting into constituent events,
    which is the expected input for repository.write
    """

    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)
    processed_records = deque()

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: deserialize_event(record),
        max_records=max_records,
    )

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        s3_input_path=s3_input_path,
        exception=exception,
    )


def handler(event: dict, context):
    worker_event = WorkerEvent(**event)
    max_records = worker_event.max_records or CACHE.MAX_RECORDS

    response = execute_step_chain(
        action=load,
        s3_client=CACHE.S3_CLIENT,
        s3_input_path=CACHE.ENVIRONMENT.s3_path(WorkerKey.LOAD),
        s3_output_path=None,
        unprocessed_dumper=pkl_dump_lz4,
        processed_dumper=CACHE.REPOSITORY.write,
        max_records=max_records,
    )
    return asdict(response)
