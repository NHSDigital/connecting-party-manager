import json
from collections import deque
from dataclasses import asdict
from io import BytesIO
from typing import TYPE_CHECKING

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.io import EtlEncoder, pkl_dump_lz4
from etl_utils.ldif.ldif import filter_and_group_ldif_from_s3_by_property, parse_ldif
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
def _read(s3_client: "S3Client", s3_input_path: str) -> deque[tuple[dict]]:
    filtered_ldif_by_group = filter_and_group_ldif_from_s3_by_property(
        s3_path=s3_input_path,
        filter_terms=FILTER_TERMS,
        group_field="nhsMhsPartyKey",
        s3_client=s3_client,
    )
    return deque(
        tuple(parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif))
        for filtered_ldif in filtered_ldif_by_group
    )


def extract(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    unprocessed_records = _read(s3_client=s3_client, s3_input_path=s3_input_path)
    processed_records = deque([])

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: [[parse_sds_record(*r).dict() for r in record]],
        record_serializer=lambda dns_and_records: json_loads(
            json.dumps([r[1] for r in dns_and_records], cls=EtlEncoder)
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
        unprocessed_dumper=lambda **kwargs: None,
        processed_dumper=pkl_dump_lz4,
    )
    return asdict(response)
