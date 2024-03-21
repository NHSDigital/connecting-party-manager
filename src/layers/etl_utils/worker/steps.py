from collections import deque
from types import FunctionType
from typing import TYPE_CHECKING

from etl_utils.smart_open import smart_open
from event.step_chain import StepChain

from .model import WorkerActionResponse

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def execute_action(data: dict, cache: dict) -> WorkerActionResponse:
    action, s3_client, s3_input_path, s3_output_path, kwargs = data[StepChain.INIT]
    return action(
        s3_client=s3_client,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
        **kwargs
    )


def _save_records_to_s3(
    s3_client: "S3Client", s3_path: str, dumper: FunctionType, records: deque
):
    with smart_open(s3_path=s3_path, mode="wb", s3_client=s3_client) as f:
        dumper(fp=f, obj=records)


def save_unprocessed_records(data: dict, cache: dict):
    action_response: WorkerActionResponse
    action_response, s3_client, dumper, _ = data[StepChain.INIT]
    _save_records_to_s3(
        s3_client=s3_client,
        s3_path=action_response.s3_input_path,
        dumper=dumper,
        records=action_response.unprocessed_records,
    )


def save_processed_records(data: dict, cache: dict):
    action_response: WorkerActionResponse
    action_response, s3_client, _, dumper = data[StepChain.INIT]
    if action_response.s3_output_path is not None:
        _save_records_to_s3(
            s3_client=s3_client,
            s3_path=action_response.s3_output_path,
            dumper=dumper,
            records=action_response.processed_records,
        )
    elif action_response.processed_records:
        dumper(action_response.processed_records)
