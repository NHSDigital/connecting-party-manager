from dataclasses import dataclass
from typing import ContextManager

from behave.model import Table
from behave.runner import Context as BehaveContext
from requests import Response

from feature_tests.end_to_end.steps.postman import PostmanCollection, PostmanItem
from feature_tests.feature_test_helpers import TestMode


@dataclass
class Context(BehaveContext):
    base_url: str
    headers: dict[str, dict[str, str]] = None
    response: Response = None
    table: Table = None
    test_mode: TestMode = None
    table_name: str = None
    session: ContextManager = None

    postman_collection: PostmanCollection = None
    postman_feature: PostmanItem = None
    postman_scenario: PostmanItem = None
    postman_step: PostmanItem = None
