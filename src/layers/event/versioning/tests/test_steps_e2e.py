from types import FunctionType
from unittest import mock

import pytest
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.step_chain import StepChain
from event.versioning.models import LambdaEventForVersioning, VersionHeader
from event.versioning.steps import versioning_steps
from nhs_context_logging.fixtures import log_capture, log_capture_global  # noqa: F401

from .example_api import index
from .example_api.src.v0.steps import steps as v0_steps
from .example_api.src.v1.steps import steps as v1_steps
from .example_api.src.v3.steps import steps as v3_steps


@mock.patch("event.versioning.steps.API_ROOT_DIRNAME", "event/versioning/tests")
@pytest.mark.parametrize(
    ("requested_version", "expected_steps"),
    (
        ["0", v0_steps],
        ["1", v1_steps],
        ["2", v1_steps],
        ["3", v3_steps],
    ),
)
def test_versioning_steps(requested_version: str, expected_steps: list[FunctionType]):
    setup_logger(service_name=f"test_versioning_steps-{requested_version}")

    _event = LambdaEventForVersioning(
        headers=VersionHeader(
            version=requested_version,
        ),
    )

    step_chain = StepChain(
        step_chain=versioning_steps, step_decorators=logging_step_decorators
    )
    step_chain.run(init={"event": _event.dict(), "api_index_file_path": index.__file__})
    assert step_chain.result is expected_steps
