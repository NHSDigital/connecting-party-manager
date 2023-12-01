from dataclasses import dataclass

from behave.model import Table
from behave.runner import Context as BehaveContext
from requests import Response

from feature_tests.end_to_end.steps.postman import (
    FeatureItem,
    PostmanCollection,
    ScenarioItem,
    StepItem,
)


@dataclass
class Context(BehaveContext):
    base_url: str
    headers: dict[str, dict[str, str]] = None
    response: Response = None
    table: Table = None

    postman_collection: PostmanCollection = None
    postman_feature: FeatureItem = None
    postman_scenario: ScenarioItem = None
    postman_step: StepItem = None
