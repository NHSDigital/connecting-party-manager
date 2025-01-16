from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING

import boto3
from domain.core.event import ExportedEventTypeDef
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from sds.epr.updates.change_request_routing import process_change_request
from sds.epr.updates.etl_device_repository import EtlDeviceRepository

from etl.sds.worker.update.transform_update.utils import export_events

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class TransformWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str
    TABLE_NAME: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


S3_CLIENT = boto3.client("s3")
DB_CLIENT = dynamodb_client()
ENVIRONMENT = TransformWorkerEnvironment.build()
REPO_KWARGS = dict(table_name=ENVIRONMENT.TABLE_NAME, dynamodb_client=DB_CLIENT)
REPOSITORIES = dict(
    etl_device_repository=EtlDeviceRepository(**REPO_KWARGS),
    product_team_repository=ProductTeamRepository(**REPO_KWARGS),
    product_repository=CpmProductRepository(**REPO_KWARGS),
    device_repository=DeviceRepository(**REPO_KWARGS),
    device_reference_data_repository=DeviceReferenceDataRepository(**REPO_KWARGS),
)
QUESTIONNAIRES = dict(
    mhs_device_questionnaire=QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS
    ),
    mhs_device_field_mapping=QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS
    ),
    accredited_system_questionnaire=QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS
    ),
    accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    ),
    message_set_questionnaire=QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    ),
    message_set_field_mapping=QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    ),
    additional_interactions_questionnaire=QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    ),
    additional_interactions_field_mapping=QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    ),
)


def transform(
    s3_client: "S3Client",
    s3_input_path: str,
    s3_output_path: str,
    max_records: int,
):
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)

    with smart_open(s3_path=s3_output_path, s3_client=s3_client) as f:
        processed_records: deque[ExportedEventTypeDef] = pkl_load_lz4(f)

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: export_events(
            process_change_request(record=record, **REPOSITORIES, **QUESTIONNAIRES)
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
