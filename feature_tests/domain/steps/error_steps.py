from behave import then
from pydantic import ValidationError

from feature_tests.domain.steps.common import assert_type_matches
from feature_tests.domain.steps.context import Context
from feature_tests.end_to_end.steps.assertion import assert_equal


@then("the error is ValidationError on fields")
def step_impl(context: Context):
    validation_error = context.error

    if not isinstance(validation_error, ValidationError):
        assertion_error = AssertionError(
            f"Expected ValidationError, got {type(validation_error)}"
        )
        raise ExceptionGroup("", (assertion_error, validation_error))
    error_fields = list(
        ".".join((validation_error.model.__name__, *error["loc"]))
        for error in validation_error.errors()
    )
    assert_equal(received=sorted(error_fields), expected=sorted(context.table.headings))


@then("the error is {err:String}")
def step_impl(context: Context, err):
    error = context.error
    assert error, f"Expected error: {err}"
    assert_type_matches(obj=error, expected_type_name=err)
