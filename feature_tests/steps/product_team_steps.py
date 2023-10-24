from behave import when
from domain.core.error import NotFoundError

from feature_tests.steps.common import catch_errors


@when(
    'User "{user_id}" creates Product Team {id:UUID} called "{name:String}" for supplier {ods_code:OdsCode}'
)
@catch_errors
def step_impl(context, user_id, id, name, ods_code):
    if user_id not in context.users:
        raise NotFoundError("Unknown User")
    if ods_code not in context.ods_organisations:
        raise NotFoundError("Unknown ODS Organisation")
    owner = context.users[user_id]
    context.subject = context.ods_organisations[ods_code]
    (result, event) = context.subject.create_product_team(id, name, owner)
    context.result = result
    context.events.append(event)
