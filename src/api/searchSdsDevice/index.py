from api_utils.api_step_chain import execute_step_chain
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger

from .src.v1.steps import mocked_steps
from .src.v1.steps import steps as v1_steps


class Environment(BaseEnvironment):
    DYNAMODB_TABLE: str


versioned_steps = {"1": v1_steps}
mocked_versioned_steps = {"1": mocked_steps}
cache = {
    **Environment.build().dict(),
    "DYNAMODB_CLIENT": dynamodb_client(),
}


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)
    query_params = event.get("queryStringParameters")
    if "use_mock" in query_params:
        return execute_step_chain(
            event=event,
            cache=cache,
            versioned_steps=mocked_versioned_steps,
        )

    return execute_step_chain(
        event=event,
        cache=cache,
        versioned_steps=versioned_steps,
    )
