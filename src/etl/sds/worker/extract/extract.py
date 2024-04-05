import json
from collections import deque
from dataclasses import asdict
from io import BytesIO
from typing import TYPE_CHECKING

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.io import EtlEncoder, pkl_dump_lz4, pkl_load_lz4
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property, ldif_dump, parse_ldif
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEnvironment
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.json import json_loads
from nhs_context_logging import log_action
from sds.domain.constants import FILTER_TERMS
from sds.domain.parse import parse_sds_record

_log_action_without_inputs = lambda function: log_action(log_args=[], log_result=False)(
    function
)

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


S3_CLIENT = boto3.client("s3")
ENVIRONMENT = WorkerEnvironment.build()


@_log_action_without_inputs
def _read(s3_client: "S3Client", s3_input_path: str) -> deque[dict]:
    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_path=s3_input_path, filter_terms=FILTER_TERMS, s3_client=s3_client
    )
    return deque(parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif))


def extract(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str
) -> WorkerActionResponse:
    unprocessed_records = _read(s3_client=s3_client, s3_input_path=s3_input_path)

    with smart_open(s3_client=s3_client, s3_path=s3_output_path) as f:
        processed_records: deque[dict] = pkl_load_lz4(f)

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: parse_sds_record(*record).dict(),
        record_serializer=lambda dn_and_record: json_loads(
            json.dumps(dn_and_record[1], cls=EtlEncoder)
        ),
    )

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        exception=exception,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
    )


def handler(event, context):
    response = execute_step_chain(
        action=extract,
        s3_client=S3_CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.EXTRACT),
        s3_output_path=ENVIRONMENT.s3_path(WorkerKey.TRANSFORM),
        unprocessed_dumper=ldif_dump,
        processed_dumper=pkl_dump_lz4,
    )
    return asdict(response)
