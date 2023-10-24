from behave import given
from domain.core.error import DuplicateError
from domain.core.root import Root


def _add_ods_to_context(context, id: str, name: str):
    if id in context.ods_organisations:
        raise DuplicateError("Invalid test: ODS Organisation exists")
    context.ods_organisations[id] = Root.create_ods_organisation(id, name)


@given('ODS Organisation {id:OdsCode} called "{name:String}"')
def step_impl(context, id: str, name: str):
    _add_ods_to_context(context, id, name)


@given("ODS Organisations")
def step_impl(context):
    for row in context.table:
        _add_ods_to_context(context, row["ods_code"], row["name"])
