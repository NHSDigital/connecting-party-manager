import json
from collections import deque
from dataclasses import asdict
from io import BytesIO

import boto3
from etl_utils.constants import WorkerKey
from etl_utils.json import SetEncoder, json_dump_bytes
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property, ldif_dump, parse_ldif
from etl_utils.worker.model import WorkerActionResponse, WorkerEnvironment
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.json import json_load, json_loads
from sds.domain.constants import FILTER_TERMS
from sds.domain.parse import parse_sds_record
from smart_open import open as _smart_open

CLIENT = boto3.client("s3")
ENVIRONMENT = WorkerEnvironment.build()


def extract(s3_client, s3_input_path: str, s3_output_path: str) -> WorkerActionResponse:
    # Read unprocessed records
    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_path=s3_input_path, filter_terms=FILTER_TERMS, s3_client=s3_client
    )
    unprocessed_records = deque(
        parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)
    )

    # Read processed records
    with _smart_open(s3_output_path) as f:
        processed_records: list[dict] = json_load(f)

    index = 0
    exception = None
    while unprocessed_records and exception is None:
        distinguished_name, record = unprocessed_records[0]
        try:
            sds_record = parse_sds_record(
                distinguished_name=distinguished_name, record=record
            )
        except Exception as _exception:
            _record = json_loads(json.dumps(record, cls=SetEncoder))
            _exception.add_note(f"Failed to parse record {index}\n{_record}")
            exception = _exception
        else:
            processed_records.append(sds_record.dict())
            unprocessed_records.popleft()
            index += 1

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
        s3_client=CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.EXTRACT),
        s3_output_path=ENVIRONMENT.s3_path(WorkerKey.TRANSFORM),
        unprocessed_dumper=ldif_dump,
        processed_dumper=json_dump_bytes,
    )
    return asdict(response)
