import json
import time
from collections import deque

import boto3
import pytest
from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from etl_utils.constants import ETL_STATE_MACHINE_HISTORY
from event.json import json_loads
from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef

from test_helpers.s3 import _set_etl_content, _set_etl_content_config
from test_helpers.terraform import read_terraform_output

TEST_DATA_NAME = "123.ldif"
EXPECTED_CHANGELOG_NUMBER = 123
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()


@pytest.mark.timeout(60)
@pytest.mark.integration
@pytest.mark.parametrize(
    ("history_object"),
    [
        ("bulk.0.123.2024-07-03T14.04.12.721948"),
        ("update.123.321.2024-07-03T14.04.12.721948"),
    ],
)
def test_manual_trigger(history_object):
    # Where the state is located
    bucket_config = _set_etl_content_config()
    manual_trigger_arn = read_terraform_output("manual_trigger_arn.value")
    expected = history_object.split(".")
    expected_prefix = ".".join(expected[:3])

    # Set some questions
    s3_client = boto3.client("s3")
    _set_etl_content(s3_client=s3_client, bucket_config=bucket_config)

    # Assert history folder empty
    state_machine_bucket_contents = s3_client.list_objects(
        Bucket=bucket_config["etl_bucket"], Prefix=f"{ETL_STATE_MACHINE_HISTORY}/"
    )
    assert "Contents" not in state_machine_bucket_contents

    # set up test (add file to history bucket)
    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"],
        Key=f"{ETL_STATE_MACHINE_HISTORY}/{history_object}",
        Body=GOOD_SDS_RECORD,
    )

    # manually trigger
    lambda_client = boto3.client("lambda")
    payload = {}
    response: InvocationResponseTypeDef = lambda_client.invoke(
        FunctionName=manual_trigger_arn,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    response_payload = response["Payload"]
    response_payload_json = json_loads(response_payload.read().decode("utf-8"))
    assert response_payload_json == "pass"
    stepfunctions_client = boto3.client("stepfunctions")
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    time.sleep(15)  # Wait for current run to finish/status successful
    executions = stepfunctions_client.list_executions(
        stateMachineArn=state_machine_arn, maxResults=1
    )
    if executions["executions"]:  # Ensure there's at least one execution
        execution = executions["executions"][0]  # Get the first (and only) execution
        result = execution["name"].split(".")
        result_prefix = ".".join(result[:3])
        assert (
            result_prefix == expected_prefix
        )  # Ensure the latest execution was the rerun expected

    state_machine_history_files = s3_client.list_objects(
        Bucket=bucket_config["etl_bucket"], Prefix=f"{ETL_STATE_MACHINE_HISTORY}/"
    )
    item_count = 0
    for item in state_machine_history_files.get("Contents", []):
        item_count = item_count + 1
        assert expected_prefix in item["Key"]
    assert item_count == 2
