import boto3

from feature_tests.end_to_end.steps.context import Context
from test_helpers.aws_session import aws_session
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def before_scenario(context: Context, scenario):
    context.base_url = read_terraform_output("invoke_url.value") + "/"
    context.headers = {}

    table_name = read_terraform_output("dynamodb_table_name.value")
    with aws_session():
        client = boto3.client("dynamodb")
        clear_dynamodb_table(client=client, table_name=table_name)
