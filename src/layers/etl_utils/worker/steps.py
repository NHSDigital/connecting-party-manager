from types import FunctionType

from event.step_chain import StepChain
from smart_open import open as _smart_open

from .model import WorkerActionResponse


def execute_action(data: dict, cache: dict) -> WorkerActionResponse:
    action, client, s3_input_path, s3_output_path = data[StepChain.INIT]
    return action(
        s3_client=client, s3_input_path=s3_input_path, s3_output_path=s3_output_path
    )


def _save_records(s3_client, s3_path: str, dumper: FunctionType, records: list):
    with _smart_open(s3_path, "wb", transport_params={"client": s3_client}) as f:
        dumper(fp=f, obj=records)


def save_unprocessed_records(data: dict, cache: dict):
    action_response: WorkerActionResponse
    action_response, s3_client, dumper, _ = data[StepChain.INIT]
    _save_records(
        s3_client=s3_client,
        s3_path=action_response.s3_input_path,
        dumper=dumper,
        records=action_response.unprocessed_records,
    )


def save_processed_records(data: dict, cache: dict):
    action_response: WorkerActionResponse
    action_response, s3_client, _, dumper = data[StepChain.INIT]
    _save_records(
        s3_client=s3_client,
        s3_path=action_response.s3_output_path,
        dumper=dumper,
        records=action_response.processed_records,
    )
