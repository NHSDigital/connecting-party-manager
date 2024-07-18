import json
import time
from collections import deque
from datetime import datetime, timezone

import boto3
import pytest
from etl_utils.constants import ETL_STATE_MACHINE_HISTORY
from event.json import json_loads
from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef

from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from test_helpers.s3 import _set_etl_content, _set_etl_content_config
from test_helpers.terraform import read_terraform_output

TEST_DATA_NAME = "123.ldif"
EXPECTED_CHANGELOG_NUMBER = 123
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()


@pytest.mark.timeout(20)
@pytest.mark.integration
@pytest.mark.parametrize(
    ("history_object"),
    [
        ("bulk.0.123.2024-07-03T14.04.12.721948"),
        ("update.100.123.2024-07-03T14.04.12.721948"),
    ],
)
def test_manual_trigger(history_object):
    # Where the state is located
    bucket_config = _set_etl_content_config()
    manual_trigger_arn = read_terraform_output("manual_trigger_arn.value")

    # Set some questions
    s3_client = boto3.client("s3")
    _set_etl_content(s3_client=s3_client, bucket_config=bucket_config, bulk=False)

    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"],
        Key=f"{ETL_STATE_MACHINE_HISTORY}/{history_object}",
        Body=GOOD_SDS_RECORD,
    )

    lambda_client = boto3.client("lambda")
    payload = {}

    # manually trigger
    start_time = datetime.now(timezone.utc)
    response: InvocationResponseTypeDef = lambda_client.invoke(
        FunctionName=manual_trigger_arn,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    response_payload = response["Payload"]
    response_payload_json = json_loads(response_payload.read().decode("utf-8"))
    assert response_payload_json == "pass"
    time.sleep(2)
    expected = history_object.split(".")
    expected_prefix = ".".join(expected[:3])

    queue_history_files = s3_client.list_objects(
        Bucket=bucket_config["etl_bucket"], Prefix=ETL_STATE_MACHINE_HISTORY
    )
    item_count = 0
    for item in queue_history_files.get("Contents", []):
        item_count = item_count + 1
        assert expected_prefix in item["Key"]
    assert item_count == 2

    stepfunctions_client = boto3.client("stepfunctions")
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    executions = stepfunctions_client.list_executions(
        stateMachineArn=state_machine_arn, maxResults=5
    )
    for execution in executions["executions"]:
        if execution["startDate"].replace(tzinfo=timezone.utc) > start_time:
            result = execution["name"].split(".")
            result_prefix = ".".join(result[:3])
            assert result_prefix == expected_prefix


# @pytest.mark.timeout(20)
# @pytest.mark.integration
# def test_execution_not_allowed_when_execution_running():
#     # Where the state is located
#     bucket_config = _set_etl_content_config()
#     table_name = bucket_config["table_name"]

#     client = dynamodb_client()
#     repository = MockDeviceRepository(table_name=table_name, dynamodb_client=client)

#     s3_client = boto3.client("s3")
#     ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=bucket_config["etl_bucket"])
#     ask_s3_prefix = partial(
#         _ask_s3_prefix, s3_client=s3_client, bucket=bucket_config["etl_bucket"]
#     )

#     was_trigger_key_deleted = lambda: not ask_s3(
#         key=bucket_config["initial_trigger_key"]
#     )
#     was_queue_history_created = lambda: ask_s3_prefix(
#         key_prefix=f"{bucket_config['queue_history_key_prefix']}/bulk",
#         question=lambda x: x == GOOD_SDS_RECORD.encode(),
#     )
#     was_state_machine_history_created = lambda: ask_s3_prefix(
#         key_prefix=f"{bucket_config['state_machine_history_key_prefix']}/bulk",
#         question=lambda x: x == GOOD_SDS_RECORD.encode(),
#     )
#     was_changelog_number_updated = lambda: ask_s3(
#         key=CHANGELOG_NUMBER,
#         question=lambda x: json_loads(x) == EXPECTED_CHANGELOG_NUMBER,
#     )
#     was_state_machine_successful = (
#         lambda: ask_s3(
#             key=WorkerKey.EXTRACT,
#             question=lambda x: x == b"",
#         )
#         and ask_s3(
#             key=WorkerKey.TRANSFORM,
#             question=lambda x: pkl_loads_lz4(x) == deque(),
#         )
#         and ask_s3(
#             key=WorkerKey.LOAD,
#             question=lambda x: pkl_loads_lz4(x) == deque(),
#         )
#         and repository.count(by=DeviceType.PRODUCT) > 0
#     )
#     was_etl_state_lock_removed = lambda: not ask_s3(key=ETL_STATE_LOCK)

#     _set_etl_content(s3_client=s3_client, bucket_config=bucket_config, bulk=True)
#     s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=CHANGELOG_NUMBER)
#     s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=ETL_STATE_LOCK)
#     clear_dynamodb_table(client=client, table_name=bucket_config["table_name"])

#     # Trigger the bulk load
#     s3_client.put_object(
#         Bucket=bucket_config["etl_bucket"],
#         Key=bucket_config["initial_trigger_key"],
#         Body=GOOD_SDS_RECORD.encode(),
#     )

#     trigger_key_deleted = False
#     queue_history_created = False
#     state_machine_history_created = False
#     changelog_number_updated = False
#     state_machine_successful = False
#     etl_state_lock_removed = False
#     while not all(
#         (
#             trigger_key_deleted,
#             queue_history_created,
#             state_machine_history_created,
#             changelog_number_updated,
#             state_machine_successful,
#             etl_state_lock_removed,
#         )
#     ):
#         time.sleep(5)
#         trigger_key_deleted = trigger_key_deleted or was_trigger_key_deleted()
#         queue_history_created = queue_history_created or was_queue_history_created()
#         state_machine_history_created = (
#             state_machine_history_created or was_state_machine_history_created()
#         )
#         changelog_number_updated = (
#             changelog_number_updated or was_changelog_number_updated()
#         )
#         state_machine_successful = (
#             state_machine_successful or was_state_machine_successful()
#         )
#         etl_state_lock_removed = etl_state_lock_removed or was_etl_state_lock_removed()

#     # Confirm the final state
#     assert trigger_key_deleted
#     assert queue_history_created
#     assert state_machine_history_created
#     assert changelog_number_updated
#     assert state_machine_successful
#     assert etl_state_lock_removed
