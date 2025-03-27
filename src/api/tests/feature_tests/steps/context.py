from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Optional

from behave.model import Table
from behave.runner import Context as BehaveContext
from mypy_boto3_dynamodb import DynamoDBClient
from requests import Response

from api.tests.feature_tests.feature_test_helpers import TestMode
from api.tests.feature_tests.steps.postman import (
    PostmanCollection,
    PostmanEnvironment,
    PostmanItem,
)


@dataclass
class Context(BehaveContext):
    base_url: str
    headers: Optional[dict[str, dict[str, str]]]
    response: Optional[Response]
    table: Optional[Table]
    test_mode: Optional[TestMode]
    table_name: Optional[str]
    session: Optional[AbstractContextManager]
    dynamodb_client: Optional[DynamoDBClient]
    workspace: Optional[str]
    environment: Optional[str]
    workspace_type: Optional[str]
    api_key: Optional[str]
    notes: Optional[dict[str, str]]
    postman_endpoint: Optional[str]

    postman_collection: PostmanCollection = None
    postman_feature: PostmanItem = None
    postman_scenario: PostmanItem = None
    postman_step: PostmanItem = None

    postman_environment: PostmanEnvironment = None
