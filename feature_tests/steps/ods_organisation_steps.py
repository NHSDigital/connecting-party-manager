from behave import given, then, when
from domain.core.root import Root

from feature_tests.steps.common import catch_errors
from feature_tests.steps.context import Context


def _add_ods_org_to_context(context: Context, ods_code: str, name: str):
    context.ods_organisations[ods_code] = Root.create_ods_organisation(
        ods_code=ods_code, name=name
    )


@given('ODS Organisation {ods_code:OdsCode} called "{name:String}"')
def step_impl(context: Context, ods_code: str, name: str):
    _add_ods_org_to_context(context=context, ods_code=ods_code, name=name)


@given("ODS Organisations")
def step_impl(context: Context):
    for row in context.table:
        _add_ods_org_to_context(
            context=context, ods_code=row["ods_code"], name=row["name"]
        )


@when('ODS Organisation {ods_code} called "{name:String}" is created')
def step_impl(context: Context, ods_code: str, name: str):
    __add_ods_org_to_context = catch_errors(_add_ods_org_to_context)
    __add_ods_org_to_context(context=context, ods_code=ods_code, name=name)


@then("ODS Organisation {ods_code} exists")
def step_impl(context: Context, ods_code: str):
    assert (
        ods_code in context.ods_organisations
    ), f"'{ods_code}' not found in organisations '{context.ods_organisations}'"
