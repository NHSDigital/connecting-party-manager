from behave import when

from feature_tests.steps.common import catch_errors
from feature_tests.steps.context import Context


@when(
    'User "{user_id}" creates Product Team {id:UUID} called "{name:String}" for supplier {ods_code:OdsCode}'
)
@catch_errors
def step_impl(context: Context, user_id, id, name, ods_code):
    context.subject = context.ods_organisations[ods_code]
    product_team = context.subject.create_product_team(id=id, name=name)
    context.result = product_team
