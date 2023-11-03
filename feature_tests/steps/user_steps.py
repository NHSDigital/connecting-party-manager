from behave import given
from domain.core.root import Root

from feature_tests.steps.context import Context


def _add_user_to_context(context: Context, id: str, name: str):
    context.users[id] = Root.create_user(id, name)


@given('User "{id}" called "{name:String}"')
def step_impl(context: Context, id: str, name: str):
    _add_user_to_context(context, id, name)


@given("Users")
def step_impl(context: Context):
    for row in context.table:
        _add_user_to_context(context, row["user_id"], row["name"])
