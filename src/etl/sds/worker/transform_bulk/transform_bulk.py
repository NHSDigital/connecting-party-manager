from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from domain.core.device.v2 import Device
from domain.core.event import ExportedEventTypeDef
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.environment import BaseEnvironment
from sds.cpm_translation import translate

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class TransformWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


S3_CLIENT = boto3.client("s3")
ENVIRONMENT = TransformWorkerEnvironment.build()


def export_devices(devices: list[Device]) -> list[dict]:
    """
    Serialises the current state of provided devices as dictionaries.
    This is needed for the transform lambda in "bulk" mode.
    """
    _devices = [device.state() for device in devices]
    return _devices


def transform(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    """
    Note that 'bulk' flag is passed through `translate` in order to optimise adding
    tags to Device. See more details in `set_device_tags_bulk` by clicking through
    `translate`.
    """
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)

    with smart_open(s3_path=s3_output_path, s3_client=s3_client) as f:
        processed_records: deque[ExportedEventTypeDef] = pkl_load_lz4(f)

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: export_devices(
            translate(obj=record, repository=None, bulk=True)
        ),
        max_records=max_records,
    )

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        exception=exception,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
    )


def handler(event: dict, context):
    _event = WorkerEvent(**event)
    response = execute_step_chain(
        action=transform,
        s3_client=S3_CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.TRANSFORM),
        s3_output_path=ENVIRONMENT.s3_path(WorkerKey.LOAD),
        unprocessed_dumper=pkl_dump_lz4,
        processed_dumper=pkl_dump_lz4,
        max_records=_event.max_records,
    )
    return asdict(response)
