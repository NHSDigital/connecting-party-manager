from behave import when

from feature_tests.domain.steps.common import catch_errors
from feature_tests.domain.steps.context import Context
from feature_tests.end_to_end.steps.table import parse_table


@when('Product Team "{id}" creates a Device with')
@catch_errors
def step_impl(context: Context, id):
    _device = parse_table(context.table)
    device_keys = _device.pop("keys", [])
    device = context.product_teams[id].create_device(**_device)
    for _device_key in device_keys:
        device.add_key(**_device_key)
    context.result = device
