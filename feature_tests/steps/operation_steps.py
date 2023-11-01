from behave import then

from feature_tests.steps.context import Context


@then("the operation is successful")
def step_impl(context: Context):
    assert context.error is None, f"Unexpected error: {context.error}"


@then("the operation is not successful")
def step_impl(context: Context):
    assert context.error is not None, "Error not found"
