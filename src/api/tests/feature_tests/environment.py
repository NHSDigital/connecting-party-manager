import time
from contextlib import nullcontext
from pathlib import Path

import click
from behave import use_fixture
from behave.model import Feature, Scenario, Step
from event.aws.client import dynamodb_client

from api.tests.feature_tests.feature_test_helpers import TestMode
from api.tests.feature_tests.steps.context import Context
from api.tests.feature_tests.steps.fixtures import (
    mock_dynamodb_cpm,
    mock_environment,
    mock_requests,
)
from api.tests.feature_tests.steps.postman import (
    BASE_URL,
    PostmanCollection,
    PostmanEnvironment,
    PostmanEnvironmentValue,
    PostmanItem,
)
from api.tests.smoke_tests.utils import get_app_key, get_base_url
from test_helpers.aws_session import aws_session
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output

PATH_TO_HERE = Path(__file__).parent
LOCAL_TABLE_NAME = "my-table"
GENERIC_SCENARIO_DESCRIPTION = "The following steps demonstrate this scenario:"


def before_all(context: Context):
    clear_screen = context.config.userdata.get("clear_screen", "false")
    context.clear_screen = clear_screen.lower() == "true"
    context.postman_collection = PostmanCollection()
    context.test_mode = TestMode.parse(config=context.config)
    context.table_name = LOCAL_TABLE_NAME
    context.base_url = BASE_URL
    context.session = nullcontext
    context.headers = {}
    context.workspace = ""
    context.workspace_type = ""
    context.environment = ""
    context.notes = {}
    context.api_key = ""  # pragma: allowlist secret
    context.postman_environment = PostmanEnvironment(
        values=[
            PostmanEnvironmentValue(key="baseUrl", value=""),
            PostmanEnvironmentValue(key="apiKey", value=""),
        ]
    )

    if context.test_mode is TestMode.INTEGRATION:
        context.workspace_type = read_terraform_output("workspace_type.value")
        context.workspace = read_terraform_output("workspace.value")
        context.environment = read_terraform_output("environment.value")
        context.base_url = (
            get_base_url(workspace=context.workspace, environment=context.environment)
            + "/"
        )
        context.session = aws_session

        with context.session():
            context.api_key = get_app_key(environment=context.environment)

        context.postman_environment = PostmanEnvironment(
            values=[
                PostmanEnvironmentValue(key="baseUrl", value=context.base_url),
                PostmanEnvironmentValue(key="apiKey", value=context.api_key),
            ]
        )

    if context.test_mode is TestMode.LOCAL:
        use_fixture(mock_environment, context=context, table_name=context.table_name)
        use_fixture(mock_requests, context=context)


def before_feature(context: Context, feature: Feature):
    context.postman_feature = PostmanItem(
        name=feature.name,
        description=" ".join(feature.description),
    )
    cpm_scenarios = [
        "Create Product Team - success scenarios",
        "Create Product Team - failure scenarios",
        "Read Product Team - success scenarios",
        "Read Product Team - failure scenarios",
        "Delete Product Team - success scenarios",
        "Delete Product Team - failure scenarios",
        "Create CPM Product - success scenarios",
        "Create CPM Product - failure scenarios",
        "Read CPM Product - success scenarios",
        "Read CPM Product - failure scenarios",
        "Delete CPM Product - success scenarios",
        "Delete CPM Product - failure scenarios",
        "Search Products - success scenarios",
        "Search Products - failures scenarios",
    ]
    if context.test_mode is TestMode.INTEGRATION:
        table = "dynamodb_cpm_table_name.value"
        context.table_name = read_terraform_output(table)
    else:
        context.table_name = LOCAL_TABLE_NAME
        use_fixture(mock_dynamodb_cpm, context=context, table_name=context.table_name)


def before_scenario(context: Context, scenario: Scenario):
    context.postman_scenario = PostmanItem(
        name=scenario.name,
        description=GENERIC_SCENARIO_DESCRIPTION,
    )
    with context.session():
        client = dynamodb_client()
        clear_dynamodb_table(client=client, table_name=context.table_name)


def before_step(context: Context, step: Step):
    context.postman_endpoint = None
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
    if context.clear_screen:
        click.clear()
        time.sleep(0.5)


def after_all(context: Context):
    context.postman_collection.save(path=PATH_TO_HERE)
    context.postman_environment.save(path=PATH_TO_HERE)
