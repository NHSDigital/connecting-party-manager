from pathlib import Path

import pytest
from event.step_chain import StepChain
from event.step_chain.tests.utils import step_data
from event.versioning.constants import VERSION_HEADER_PATTERN, VERSIONING_STEP_ARGS
from event.versioning.errors import VersionException
from event.versioning.models import LambdaEventForVersioning, VersionHeader
from event.versioning.steps import get_largest_possible_version, get_requested_version
from hypothesis import given
from hypothesis.strategies import builds, dictionaries, from_regex, none, text
from pydantic import ValidationError

PATH_TO_HERE = Path(__file__).parent


@given(
    event=builds(
        LambdaEventForVersioning,
        headers=builds(
            VersionHeader,
            version=from_regex(VERSION_HEADER_PATTERN, fullmatch=True),
        ),
    )
)
def test_get_requested_version_pass(event: LambdaEventForVersioning):
    version = get_requested_version(data=step_data(init={"event": event.dict()}))
    assert version == event.headers.version


@given(event=dictionaries(keys=text(min_size=3, max_size=3), values=none()))
def test_get_requested_version_fail(event: dict):
    with pytest.raises(ValidationError):
        get_requested_version(data=step_data(init={"event": event}))


@pytest.mark.parametrize(
    "requested_version,expected_version",
    [
        ("3", "3"),
        ("4", "3"),
        ("5", "3"),
        ("6", "6"),
        ("7", "6"),
        ("8", "6"),
        ("9", "9"),
        ("1000", "9"),
        ("3.0", "3"),
        ("3.5", "3"),
        ("3.9", "3"),
        ("10000.1234", "9"),
    ],
)
def test_largest_possible_version(requested_version: str, expected_version: str):
    handler_versions = {"3": "handler3", "6": "handler6", "9": "handler9"}

    actual_version = get_largest_possible_version(
        data=step_data(
            kwargs={
                get_requested_version: requested_version,
                StepChain.INIT: {
                    VERSIONING_STEP_ARGS.VERSIONED_STEPS: handler_versions
                },
            }
        )
    )
    assert actual_version == expected_version


@pytest.mark.parametrize("requested_version", ["-2", "-1", "0", "1", "2"])
def test_largest_possible_version_error(requested_version: str):
    handler_versions = {"3": "handler3", "6": "handler6", "9": "handler9"}

    with pytest.raises(VersionException) as e:
        get_largest_possible_version(
            data=step_data(
                kwargs={
                    get_requested_version: requested_version,
                    StepChain.INIT: {
                        VERSIONING_STEP_ARGS.VERSIONED_STEPS: handler_versions
                    },
                }
            )
        )
    assert str(e.value) == "Version not supported"
