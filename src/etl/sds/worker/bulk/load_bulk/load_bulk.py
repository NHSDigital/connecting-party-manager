from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from sds.epr.bulk_create.bulk_repository import BulkRepository
from sds.worker.load import LoadWorkerEnvironment

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class LoadWorkerCache:
    def __init__(self):
        self.S3_CLIENT = boto3.client("s3")
        self.ENVIRONMENT = LoadWorkerEnvironment.build()
        self.REPOSITORY = BulkRepository(
            table_name=self.ENVIRONMENT.TABLE_NAME, dynamodb_client=dynamodb_client()
        )
        self.MAX_RECORDS = 150_000


CACHE = LoadWorkerCache()


class BulkLoadWorkerEvent(WorkerEvent):
    s3_input_path: str


def load(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    """
    For bulk, the transformed data is ready to pass to the repository.write_bulk
    so nothing to do here other than load and buffer the data from
    'unprocessed_records' to 'processed_records'
    """
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)
    processed_records = deque()

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: record,
        max_records=max_records,
    )

    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        return WorkerActionResponse(
            unprocessed_records=unprocessed_records,
            processed_records=processed_records,
            s3_input_path=s3_input_path,
            exception=exception,
        )


def handler(event: dict, context):
    worker_event = BulkLoadWorkerEvent(**event)
    max_records = worker_event.max_records or CACHE.MAX_RECORDS
    response = execute_step_chain(
        action=load,
        s3_client=CACHE.S3_CLIENT,
        s3_input_path=worker_event.s3_input_path,
        s3_output_path=None,
        unprocessed_dumper=pkl_dump_lz4,
        processed_dumper=CACHE.REPOSITORY.write,
        max_records=max_records,
    )
    return asdict(response)
