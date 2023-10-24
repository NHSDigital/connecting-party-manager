from behave import then

from feature_tests.steps.common import (
    assert_type_matches,
    parse_value,
    read_value_from_path,
)


@then("the following events were raised")
def step_impl(context):
    i = 0
    for row in context.table:
        assert i < len(context.events), "event count mismatch: too few raised"
        actual = context.events[i]
        expected = row["event"]
        assert (
            type(actual).__name__ == expected
        ), "Event expected {expected} got {actual}"
        i = i + 1
    assert len(context.events) == i, "event count mismatch: too many raised"


@then("event #{ix:Number} is {type_name:String} with")
def step_impl(context, ix, type_name):
    assert ix <= len(context.events), "Invalid event index"
    event = context.events[ix - 1]
    assert_type_matches(event, type_name)
    for row in context.table:
        path = row["property"]
        expected = parse_value(row["value"])
        actual = read_value_from_path(event, path)
        assert (
            actual == expected
        ), "Property mismatch {property}: expected {expected} got {actual}"
