import json
from collections import deque
from dataclasses import asdict
from io import BytesIO
from typing import TYPE_CHECKING

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.json import EtlEncoder, json_dump_bytes
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property, ldif_dump, parse_ldif
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEnvironment
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.json import json_load, json_loads
from sds.domain.constants import FILTER_TERMS
from sds.domain.parse import parse_sds_record

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


S3_CLIENT = boto3.client("s3")
ENVIRONMENT = WorkerEnvironment.build()


def extract(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str
) -> WorkerActionResponse:
    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_path=s3_input_path, filter_terms=FILTER_TERMS, s3_client=s3_client
    )
    unprocessed_records = deque(
        parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)
    )

    with smart_open(s3_client=s3_client, s3_path=s3_output_path) as f:
        processed_records: list[dict] = json_load(f)

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
        processed_dumper=json_dump_bytes,
    )
    return asdict(response)
