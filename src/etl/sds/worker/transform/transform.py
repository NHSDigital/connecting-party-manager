from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from domain.core.event import ExportedEventTypeDef
from domain.core.load_questionnaire import render_questionnaire
from domain.core.questionnaires import QuestionnaireInstance
from domain.repository.device_repository import DeviceRepository
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from sds.cpm_translation import translate

from etl.sds.worker.transform.reject_duplicates import reject_duplicate_keys

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class TransformWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str
    TABLE_NAME: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


S3_CLIENT = boto3.client("s3")
ENVIRONMENT = TransformWorkerEnvironment.build()
REPOSITORY = DeviceRepository(
    table_name=ENVIRONMENT.TABLE_NAME, dynamodb_client=dynamodb_client()
)


def transform(
    s3_client: "S3Client", s3_input_path: str, s3_output_path: str, max_records: int
) -> WorkerActionResponse:
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)

    with smart_open(s3_path=s3_output_path, s3_client=s3_client) as f:
        processed_records: deque[ExportedEventTypeDef] = pkl_load_lz4(f)

    spine_device_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_DEVICE, questionnaire_version=1
    )
    spine_endpoint_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT, questionnaire_version=1
    )

    _spine_device_questionnaire = spine_device_questionnaire.dict()
    _spine_endpoint_questionnaire = spine_endpoint_questionnaire.dict()

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: translate(
            obj=record,
            spine_device_questionnaire=spine_device_questionnaire,
            _spine_device_questionnaire=_spine_device_questionnaire,
            spine_endpoint_questionnaire=spine_endpoint_questionnaire,
            _spine_endpoint_questionnaire=_spine_endpoint_questionnaire,
            _trust=True,
            repository=REPOSITORY,
        ),
        max_records=max_records,
    )

    if exception is None:
        reject_duplicate_keys(exported_events=processed_records)

    return WorkerActionResponse(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        exception=exception,
        s3_input_path=s3_input_path,
        s3_output_path=s3_output_path,
    )


def handler(event: dict, context):
    max_records = WorkerEvent(**event).max_records
    response = execute_step_chain(
        action=transform,
        s3_client=S3_CLIENT,
        s3_input_path=ENVIRONMENT.s3_path(WorkerKey.TRANSFORM),
        s3_output_path=ENVIRONMENT.s3_path(WorkerKey.LOAD),
        unprocessed_dumper=pkl_dump_lz4,
        processed_dumper=pkl_dump_lz4,
        max_records=max_records,
    )
    return asdict(response)
