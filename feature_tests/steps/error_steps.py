from behave import then


@then("the error is {err:String}")
def step_impl(context, err):
    error = context.error
    assert error, f"Expected error: {err}"
    assert type(error).__name__ == err, f"Unexpected error: {type(error).__name__}"
