from contextlib import nullcontext
from pathlib import Path

from behave import use_fixture
from behave.model import Feature, Scenario, Step
from event.aws.client import dynamodb_client

from feature_tests.end_to_end.steps.context import Context
from feature_tests.end_to_end.steps.fixtures import (
    mock_dynamodb,
    mock_environment,
    mock_requests,
)
from feature_tests.end_to_end.steps.postman import (
    BASE_URL,
    PostmanCollection,
    PostmanItem,
)
from feature_tests.feature_test_helpers import TestMode
from test_helpers.aws_session import aws_session
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output

PATH_TO_HERE = Path(__file__).parent
LOCAL_TABLE_NAME = "my-table"
GENERIC_SCENARIO_DESCRIPTION = "The following steps demonstrate this scenario:"


def before_all(context: Context):
    context.postman_collection = PostmanCollection()
    context.test_mode = TestMode.parse(config=context.config)
    context.table_name = LOCAL_TABLE_NAME
    context.base_url = BASE_URL
    context.session = nullcontext
    context.headers = {}

    if context.test_mode is TestMode.INTEGRATION:
        context.table_name = read_terraform_output("dynamodb_table_name.value")
        context.base_url = read_terraform_output("invoke_url.value") + "/"
        context.session = aws_session

    if context.test_mode is TestMode.LOCAL:
        use_fixture(mock_requests, context=context)
        use_fixture(mock_dynamodb, context=context, table_name=context.table_name)
        use_fixture(mock_environment, context=context, table_name=context.table_name)


def before_feature(context: Context, feature: Feature):
    context.postman_feature = PostmanItem(
        name=feature.name,
        description=" ".join(feature.description),
    )


def before_scenario(context: Context, scenario: Scenario):
    context.postman_scenario = PostmanItem(
        name=scenario.name,
        description=GENERIC_SCENARIO_DESCRIPTION,
    )
    with context.session():
        client = dynamodb_client()
        clear_dynamodb_table(client=client, table_name=context.table_name)


def before_step(context: Context, step: Step):
    context.postman_step = PostmanItem(
        name=f"{step.keyword.lower().title()} {step.name}", item=None
    )


def after_step(context: Context, step: Step):
    context.table = None
    if context.postman_step:
        context.postman_scenario.item.append(context.postman_step)


def after_scenario(context: Context, scenario: Scenario):
    context.headers = {}
    if context.postman_scenario:
        context.postman_feature.item.append(context.postman_scenario)


def after_feature(context: Context, feature: Feature):
    if context.postman_feature:
        context.postman_collection.item.append(context.postman_feature)


def after_all(context: Context):
    context.postman_collection.save(path=PATH_TO_HERE)
