from collections import deque
from dataclasses import asdict
from itertools import batched
from types import FunctionType
from typing import TYPE_CHECKING

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse
from etl_utils.worker.steps import (
    execute_action,
    save_processed_records,
    save_unprocessed_records,
)
from etl_utils.worker.worker_step_chain import (
    _log_action_without_inputs,
    _render_response,
    log_exception,
)
from event.environment import BaseEnvironment
from event.step_chain import StepChain
from sds.epr.bulk_create.bulk_load_fanout import FANOUT, calculate_batch_size
from sds.epr.bulk_create.bulk_repository import BulkRepository

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class TransformWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


ENVIRONMENT = TransformWorkerEnvironment.build()
S3_CLIENT = boto3.client("s3")


def execute_step_chain(
    action: FunctionType,
    s3_client,
    s3_input_path: str,
    s3_output_path: str,
    unprocessed_dumper: FunctionType,
    processed_dumper: FunctionType,
    max_records: int = None,
    **kwargs,
) -> list[dict]:
    # Run the main action chain
    action_chain = StepChain(
        step_chain=[execute_action], step_decorators=[_log_action_without_inputs]
    )
    action_chain.run(
        init=(action, s3_client, s3_input_path, s3_output_path, max_records, kwargs)
    )
    if isinstance(action_chain.result, Exception):
        log_exception(action_chain.result)

    # Save the action chain results if there were no unhandled (fatal) exceptions
    count_unprocessed_records = None
    count_processed_records = None
    save_chain_response = None

    worker_response = []
    if isinstance(action_chain.result, WorkerActionResponse):
        if isinstance(action_chain.result.exception, Exception):
            log_exception(action_chain.result.exception)

        count_unprocessed_records = len(action_chain.result.unprocessed_records)

        batch_size = calculate_batch_size(
            sequence=action_chain.result.processed_records, n_batches=FANOUT
        )
        for i, batch in enumerate(
            batched(action_chain.result.processed_records, n=batch_size)
        ):
            count_processed_records = len(batch)
            _action_response = WorkerActionResponse(
                unprocessed_records=action_chain.result.unprocessed_records,
                s3_input_path=action_chain.result.s3_input_path,
                processed_records=deque(batch),
                s3_output_path=ENVIRONMENT.s3_path(f"{WorkerKey.LOAD}.{i}"),
                exception=action_chain.result.exception,
            )

            save_chain = StepChain(
                step_chain=[save_unprocessed_records, save_processed_records],
                step_decorators=[_log_action_without_inputs],
            )
            save_chain.run(
                init=(
                    _action_response,
                    s3_client,
                    unprocessed_dumper,
                    processed_dumper,
                )
            )
            save_chain_response = save_chain.result

            if isinstance(save_chain.result, Exception):
                log_exception(save_chain.result)

            # Summarise the outcome of action_chain and step_chain
            worker_response_item = _render_response(
                action_name=action.__name__,
                action_chain_response=_action_response,
                save_chain_response=save_chain_response,
                count_unprocessed_records=count_unprocessed_records,
                count_processed_records=count_processed_records,
            )
            _response = asdict(worker_response_item)
            _response["s3_input_path"] = ENVIRONMENT.s3_path(f"{WorkerKey.LOAD}.{i}")
            worker_response.append(_response)
    return worker_response


def load_bulk_fanout(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)
    processed_records = deque()

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: BulkRepository(
            None, None
        ).generate_transaction_statements(record),
        max_records=max_records,
    )

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
        exception=exception,
    )


def handler(event: dict, context):
    return execute_step_chain(
        action=load_bulk_fanout,
        s3_client=S3_CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.LOAD),
        s3_output_path=None,
        unprocessed_dumper=pkl_dump_lz4,
        processed_dumper=pkl_dump_lz4,
        max_records=None,
    )
