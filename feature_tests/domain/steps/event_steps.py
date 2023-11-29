from behave import then

from feature_tests.domain.steps.common import (
    assert_type_matches,
    parse_value,
    read_value_from_path,
)
from feature_tests.domain.steps.context import Context


@then("the following events were raised for the result")
def step_impl(context: Context):
    assert len(context.result.events) == len(
        context.table.rows
    ), f"event count mismatch: expected {len(context.table.rows)} got {len(context.subject.events)}"

    for row, event in zip(context.table, context.events):
        type_name = row["event"]
        assert_type_matches(obj=event, expected_type_name=type_name)


@then("event #{ix:Number} of the result is {type_name:String} with")
def step_impl(context: Context, ix, type_name):
    events = context.result.events
    assert ix <= len(events), "Invalid event index"
    event = events[ix - 1]
    assert_type_matches(obj=event, expected_type_name=type_name)
    for row in context.table:
        path = row["property"]
        expected = parse_value(v=row["value"])
        actual = read_value_from_path(obj=event, full_path=path)
        assert (
            actual == expected
        ), f"Property mismatch {path}: expected {expected} got {actual}"
