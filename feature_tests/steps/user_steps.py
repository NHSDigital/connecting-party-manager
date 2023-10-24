from behave import given
from domain.core.error import DuplicateError
from domain.core.root import Root


def _add_user_to_context(context, id: str, name: str):
    if id in context.users:
        raise DuplicateError("Invalid test: User already exists")
    context.users[id] = Root.create_user(id, name)


@given('User "{id}" called "{name:String}"')
def step_impl(context, id: str, name: str):
    _add_user_to_context(context, id, name)


@given("Users")
def step_impl(context):
    for row in context.table:
        _add_user_to_context(context, row["user_id"], row["name"])
