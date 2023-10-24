from behave import then


@then("the operation was successful")
def step_impl(context):
    assert context.error is None, f"Unexpected error: {context.error}"


@then("the operation was not successful")
def step_impl(context):
    assert context.error, f"Expected error"
