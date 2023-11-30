import boto3
from behave.model import Feature, Scenario, Step

from feature_tests.end_to_end.steps.context import Context
from feature_tests.feature_test_helpers import TestMode
from test_helpers.aws_session import aws_session
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def before_feature(context: Context, feature: Feature):
    # At present we only run end-to-end tests in 'integration' mode
    test_mode = TestMode.parse(config=context.config)
    if test_mode is not TestMode.INTEGRATION:
        feature.mark_skipped()


def before_scenario(context: Context, scenario: Scenario):
    context.base_url = read_terraform_output("invoke_url.value") + "/"
    context.headers = {}

    table_name = read_terraform_output("dynamodb_table_name.value")
    with aws_session():
        client = boto3.client("dynamodb")
        clear_dynamodb_table(client=client, table_name=table_name)


def after_step(context: Context, step: Step):
    context.table = None
