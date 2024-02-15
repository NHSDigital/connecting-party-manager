import json
from http import HTTPStatus

from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER
from etl_utils.trigger.model import StateMachineInput


class ChangelogNumberExists(Exception):
    def __init__(self, bucket, key):
        super().__init__(
            self, f"s3://{bucket}/{key} should not exist when using bulk trigger"
        )


def validate_no_changelog_number(s3_client, source_bucket):
    try:
        s3_client.head_object(Bucket=source_bucket, Key=CHANGELOG_NUMBER)
    except ClientError as error:
        if error.response["Error"]["Code"] != str(HTTPStatus.NOT_FOUND):
            raise error
    else:
        raise ChangelogNumberExists(bucket=source_bucket, key=CHANGELOG_NUMBER)


def start_execution(
    step_functions_client,
    state_machine_arn: str,
    state_machine_input: StateMachineInput,
):
    return step_functions_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=state_machine_input.name,
        input=json.dumps(state_machine_input.dict()),
    )
