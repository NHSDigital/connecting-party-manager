import json

import boto3
from behave.model import Feature, Scenario, Step

from feature_tests.end_to_end.steps.context import Context
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


def after_all(context: Context):
    if context.postman_collection.item:
        postman_collection = context.postman_collection.dict(
            exclude_none=True, by_alias=True
        )
        with open(PROJECT_ROOT / "postman-collection.json", "w") as f:
            json.dump(fp=f, obj=postman_collection, indent=4)


def before_feature(context: Context, feature: Feature):
    context.postman_feature = FeatureItem(name=feature.name)

    # At present we only run end-to-end tests in 'integration' mode
    test_mode = TestMode.parse(config=context.config)
    if test_mode is not TestMode.INTEGRATION:
        feature.mark_skipped()


def after_feature(context: Context, scenario: Scenario):
    context.postman_collection.item.append(context.postman_feature)


def before_scenario(context: Context, scenario: Scenario):
    context.postman_scenario = ScenarioItem(name=scenario.name)

    context.base_url = read_terraform_output("invoke_url.value") + "/"
    context.headers = {}

    table_name = read_terraform_output("dynamodb_table_name.value")
    with aws_session():
        client = boto3.client("dynamodb")
        clear_dynamodb_table(client=client, table_name=table_name)


def after_scenario(context: Context, scenario: Scenario):
    context.postman_feature.item.append(context.postman_scenario)


def before_step(context: Context, step: Step):
    context.postman_step = StepItem(name=step.name)


def after_step(context: Context, step: Step):
    if context.postman_step.request is not None:
        context.postman_scenario.item.append(context.postman_step)
    context.table = None
