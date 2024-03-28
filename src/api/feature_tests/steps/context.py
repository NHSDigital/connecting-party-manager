from dataclasses import dataclass
from typing import ContextManager

from behave.model import Table
from behave.runner import Context as BehaveContext
from mypy_boto3_dynamodb import DynamoDBClient
from requests import Response

from api.feature_tests.feature_test_helpers import TestMode
from api.feature_tests.steps.postman import PostmanCollection, PostmanItem


@dataclass
class Context(BehaveContext):
    base_url: str
    headers: dict[str, dict[str, str]] = None
    response: Response = None
    table: Table = None
    test_mode: TestMode = None
    table_name: str = None
    session: ContextManager = None
    dynamodb_client: DynamoDBClient = None
    workspace: str = None
    workspace_type: str = None
    apikey: str = None

    postman_collection: PostmanCollection = None
    postman_feature: PostmanItem = None
    postman_scenario: PostmanItem = None
    postman_step: PostmanItem = None
