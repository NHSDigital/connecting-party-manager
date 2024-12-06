from collections import deque
from dataclasses import asdict
from types import FunctionType
from typing import TYPE_CHECKING

import boto3
from domain.core.aggregate_root import AggregateRoot
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dump_lz4, pkl_dumps_lz4, pkl_load_lz4
from etl_utils.smart_open import smart_open
from etl_utils.worker.action import apply_action
from etl_utils.worker.exception import truncate_message
from etl_utils.worker.model import WorkerActionResponse, WorkerEvent
from etl_utils.worker.worker_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from sds.epr.bulk_create.bulk_create import create_complete_epr_product
from sds.epr.bulk_create.bulk_load_fanout import count_indexes
from sds.epr.bulk_create.epr_product_team_repository import EprProductTeamRepository

from etl.sds.worker.bulk.transform_bulk.utils import smart_open_if_exists

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class TransformWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str
    TABLE_NAME: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


S3_CLIENT = boto3.client("s3")
ENVIRONMENT = TransformWorkerEnvironment.build()
SERIALISED_EMPTY_DEQUE = pkl_dumps_lz4(deque([]))


AS_DEVICE_QUESTIONNAIRE = QuestionnaireRepository().read(QuestionnaireInstance.SPINE_AS)
MHS_DEVICE_QUESTIONNAIRE = QuestionnaireRepository().read(
    QuestionnaireInstance.SPINE_MHS
)
MESSAGE_SETS_QUESTIONNAIRE = QuestionnaireRepository().read(
    QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
)
ADDITIONAL_INTERACTIONS_QUESTIONNAIRE = QuestionnaireRepository().read(
    QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
)
ACCREDITED_SYSTEM_FIELD_MAPPING = QuestionnaireRepository().read_field_mapping(
    QuestionnaireInstance.SPINE_AS
)
MHS_DEVICE_FIELD_MAPPING = QuestionnaireRepository().read_field_mapping(
    QuestionnaireInstance.SPINE_MHS
)
MESSAGE_SETS_FIELD_MAPPING = QuestionnaireRepository().read_field_mapping(
    QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
)
EPR_PRODUCT_TEAM_REPOSITORY = EprProductTeamRepository(
    table_name=ENVIRONMENT.TABLE_NAME, dynamodb_client=dynamodb_client()
)


def export_domain_objects(objects: list[AggregateRoot]) -> list[dict]:
    _obj = [{obj.__class__.__name__: obj.state()} for obj in objects]
    return _obj


def apply_action(
    unprocessed_records: deque,
    processed_records: deque,
    action: FunctionType,
    max_records: int = None,
):
    exception = None
    index, count_generated_records = 0, 0
    while (
        unprocessed_records
        and exception is None
        and (max_records is None or count_generated_records < max_records)
    ):
        record = unprocessed_records[0]
        try:
            domain_objects = action(record=record)
        except Exception as _exception:
            msg = truncate_message(str(record))
            _exception.add_note(f"Failed to parse record {index}\n{msg}")
            exception = _exception
        else:
            processed_records += export_domain_objects(domain_objects)
            count_generated_records += sum(count_indexes(obj) for obj in domain_objects)
            index += 1
            unprocessed_records.popleft()
    return exception


def transform(
    s3_client: "S3Client",
    s3_input_path: str,
    s3_output_path: str,
    max_records: int,
) -> WorkerActionResponse:
    with smart_open(s3_path=s3_input_path, s3_client=s3_client) as f:
        unprocessed_records: deque[dict] = pkl_load_lz4(f)

    with smart_open_if_exists(
        s3_path=s3_output_path,
        s3_client=s3_client,
        empty_content=SERIALISED_EMPTY_DEQUE,
    ) as f:
        processed_records = pkl_load_lz4(f)

    product_team_ids = {p.ods_code: p.id for p in EPR_PRODUCT_TEAM_REPOSITORY.search()}

    exception = apply_action(
        unprocessed_records=unprocessed_records,
        processed_records=processed_records,
        action=lambda record: create_complete_epr_product(
            party_key_group=record,
            mhs_device_questionnaire=MHS_DEVICE_QUESTIONNAIRE,
            message_set_questionnaire=MESSAGE_SETS_QUESTIONNAIRE,
            additional_interactions_questionnaire=ADDITIONAL_INTERACTIONS_QUESTIONNAIRE,
            accredited_system_questionnaire=AS_DEVICE_QUESTIONNAIRE,
            mhs_device_field_mapping=MHS_DEVICE_FIELD_MAPPING,
            message_set_field_mapping=MESSAGE_SETS_FIELD_MAPPING,
            accredited_system_field_mapping=ACCREDITED_SYSTEM_FIELD_MAPPING,
            product_team_ids=product_team_ids,
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
