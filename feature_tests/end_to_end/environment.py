import json

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
    FeatureItem,
    PostmanCollection,
    ScenarioItem,
    StepItem,
)
from feature_tests.feature_test_helpers import TestMode
from test_helpers.aws_session import aws_session
from test_helpers.constants import PROJECT_ROOT
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def before_all(context: Context):
    context.postman_collection = PostmanCollection()

    test_mode = TestMode.parse(config=context.config)
    if test_mode is not TestMode.INTEGRATION:
        use_fixture(mock_requests, context=context)
        use_fixture(mock_dynamodb, context=context, table_name="my-table")
        use_fixture(mock_environment, context=context, table_name="my-table")


def after_all(context: Context):
    test_mode = TestMode.parse(config=context.config)

    if context.postman_collection.item and test_mode is TestMode.INTEGRATION:
        postman_collection = context.postman_collection.dict(
            exclude_none=True, by_alias=True
        )
        with open(PROJECT_ROOT / "postman-collection.json", "w") as f:
            json.dump(fp=f, obj=postman_collection, indent=4)


def before_feature(context: Context, feature: Feature):
    context.postman_feature = FeatureItem(name=feature.name)


def after_feature(context: Context, scenario: Scenario):
    context.postman_collection.item.append(context.postman_feature)


def before_scenario(context: Context, scenario: Scenario):
    context.postman_scenario = ScenarioItem(name=scenario.name)

    context.headers = {}

    test_mode = TestMode.parse(config=context.config)
    if test_mode is TestMode.INTEGRATION:
        table_name = read_terraform_output("dynamodb_table_name.value")
        context.base_url = read_terraform_output("invoke_url.value") + "/"
        with aws_session():
            client = dynamodb_client()
            clear_dynamodb_table(client=client, table_name=table_name)
    else:
        context.base_url = ""
        client = dynamodb_client()
        clear_dynamodb_table(client=client, table_name="my-table")


def after_scenario(context: Context, scenario: Scenario):
    context.postman_feature.item.append(context.postman_scenario)


def before_step(context: Context, step: Step):
    context.postman_step = StepItem(name=f"{step.keyword.lower().title()} {step.name}")


def after_step(context: Context, step: Step):
    if context.postman_step.request is not None:
        context.postman_scenario.item.append(context.postman_step)
    context.table = None
