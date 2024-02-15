from unittest import mock

from domain.logging.step_decorators import logging_step_decorators
from event.logging.models import StepLog
from event.step_chain import StepChain
from event.step_chain.tests.utils import step_data
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_fixture as log_capture,
)
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_global_fixture as log_capture_global,
)


def test_logging_step_decorators(log_capture):
    return_value = "return value!"
    init_data = "init data!"
    cache = {"foo": "bar"}

    # Define a step
    def a_function(data, cache):
        return return_value

    # Run the step, with logging
    step_chain = StepChain(
        step_chain=[a_function], step_decorators=logging_step_decorators
    )
    step_chain.run(init=init_data, cache=cache)
    assert step_chain.result == return_value

    # Assert no error messages
    std_out, std_err = log_capture
    assert len(std_err) == 0

    # Validate the log structure
    (log,) = std_out
    parsed_log = StepLog(**log)

    # Validate the log data
    assert parsed_log.data == dict(step_data(init=init_data))
    assert (
        parsed_log.cache is not cache
    )  # Make sure that the log doesn't have a direct reference to global data
    assert parsed_log.cache == cache
    assert parsed_log.action_result == return_value
    assert (
        parsed_log.action
        == "src.layers.domain.logging.tests.test_step_decorators.a_function"
    )
    assert parsed_log.action_status == "succeeded"


def test_logging_step_decorators_with_fatal_error(log_capture):
    init_data = "init data!"
    cache = {"foo": "bar"}
    error_message = "oops!"

    class MyException(Exception):
        pass

    # Define a step
    def a_function(data, cache):
        raise MyException(error_message)

    # Run the step, with logging
    step_chain = StepChain(
        step_chain=[a_function], step_decorators=logging_step_decorators
    )
    step_chain.run(init=init_data, cache=cache)
    assert isinstance(step_chain.result, MyException)

    # Assert only error messages
    std_out, std_err = log_capture
    assert len(std_out) == 0

    # Validate the log structure
    (log,) = std_err
    parsed_log = StepLog(**log)

    # Validate the log data
    assert parsed_log.data == dict(step_data(init=init_data))
    assert (
        parsed_log.cache is not cache
    )  # Make sure that the log doesn't have a direct reference to global data
    assert parsed_log.cache == cache
    assert parsed_log.action_result == None
    assert (
        parsed_log.action
        == "src.layers.domain.logging.tests.test_step_decorators.a_function"
    )
    assert parsed_log.action_status == "failed"


def test_logging_step_decorators_with_non_fatal_error(log_capture):
    init_data = "init data!"
    cache = {"foo": "bar"}
    error_message = "oops!"

    class MyException(Exception):
        pass

    # Define a step
    def a_function(data, cache):
        raise MyException(error_message)

    # Run the step, with logging
    with mock.patch(
        "domain.logging.step_decorators.EXPECTED_EXCEPTIONS", (MyException,)
    ):
        step_chain = StepChain(
            step_chain=[a_function], step_decorators=logging_step_decorators
        )
        step_chain.run(init=init_data, cache=cache)
    assert isinstance(step_chain.result, MyException)

    # Assert no error messages
    std_out, std_err = log_capture
    assert len(std_err) == 0

    # Validate the log structure
    (log,) = std_out
    parsed_log = StepLog(**log)

    # Validate the log data
    assert parsed_log.data == dict(step_data(init=init_data))
    assert (
        parsed_log.cache is not cache
    )  # Make sure that the log doesn't have a direct reference to global data
    assert parsed_log.cache == cache
    assert parsed_log.action_result == None
    assert (
        parsed_log.action
        == "src.layers.domain.logging.tests.test_step_decorators.a_function"
    )
    assert parsed_log.action_status == "error"
