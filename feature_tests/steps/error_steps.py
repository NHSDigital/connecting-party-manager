from behave import then

from feature_tests.steps.common import assert_type_matches
from feature_tests.steps.context import Context


@then("the error is {err:String}")
def step_impl(context: Context, err):
    error = context.error
    assert error, f"Expected error: {err}"
    assert_type_matches(obj=error, expected_type_name=err)
