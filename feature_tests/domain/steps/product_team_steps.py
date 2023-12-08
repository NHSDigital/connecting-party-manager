from behave import given, when
from domain.core.root import Root

from feature_tests.domain.steps.common import catch_errors
from feature_tests.domain.steps.context import Context


def _add_product_team_to_context(context: Context, ods_code: str, **_product_team):
    org = Root.create_ods_organisation(ods_code=ods_code)
    product_team = org.create_product_team(**_product_team)
    context.product_teams[_product_team["id"]] = product_team


@given("Product Teams")
def given_product_teams(context: Context):
    for row in context.table:
        _product_team = {field: row[field] for field in context.table.headings}
        _add_product_team_to_context(context=context, **_product_team)


@when(
    'User "{user_id}" creates Product Team {id:String} called "{name:String}" for supplier {ods_code:OdsCode}'
)
@catch_errors
def step_impl(context: Context, user_id, id, name, ods_code):
    context.subject = context.ods_organisations[ods_code]
    product_team = context.subject.create_product_team(id=id, name=name)
    context.result = product_team
