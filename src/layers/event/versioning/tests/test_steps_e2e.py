from types import FunctionType

import pytest
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.step_chain import StepChain
from event.versioning.constants import VERSIONING_STEP_ARGS
from event.versioning.models import Event, VersionHeader
from event.versioning.steps import versioning_steps
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_fixture as log_capture,
)
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_global_fixture as log_capture_global,
)

from .example_api.src.v0.steps import steps as v0_steps
from .example_api.src.v1.steps import steps as v1_steps
from .example_api.src.v3.steps import steps as v3_steps

versioned_steps = {
    "0": v0_steps,
    "1": v1_steps,
    "3": v3_steps,
}


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

    _event = Event(
        headers=VersionHeader(
            version=requested_version,
        ),
    )

    step_chain = StepChain(
        step_chain=versioning_steps, step_decorators=logging_step_decorators
    )
    step_chain.run(
        init={
            VERSIONING_STEP_ARGS.EVENT: _event.dict(),
            VERSIONING_STEP_ARGS.VERSIONED_STEPS: versioned_steps,
        }
    )
    assert step_chain.result is expected_steps
