from uuid import UUID

from behave import then

from feature_tests.domain.steps.common import parse_value, read_value_from_path
from feature_tests.domain.steps.context import Context
from feature_tests.end_to_end.steps.assertion import assert_equal


@then("the result is of type {type_name}")
def step_impl(context: Context, type_name):
    t = type(context.result).__name__
    assert t == type_name, f"Expected '{type_name}' got '{t}'"


@then("the result {field} equals {value:Number}")
def step_impl(context: Context, field, value):
    assert context.result is not None, "result"
    v = context.result.__dict__[field]
    assert v == value, f"Expected {value} but found {v}"


@then('the result {field:String} equals "{value:String}"')
def step_impl(context: Context, field, value):
    assert context.result is not None, "result"
    v = context.result.__dict__[field]
    assert v == value, f"Expected {value} but found {v}"


@then("the result {field:String} equals {value:String}")
def step_impl(context: Context, field, value):
    assert context.result is not None, "result"
    v = context.result.__dict__[field]
    assert v == value, f"Expected {value} but found {v}"


def _assert_value(obj, path, value):
    [head, *tail] = path
    v = obj.__dict__[head]
    if len(tail) > 0:
        _assert_value(v, tail, value)
    else:
        assert (
            v == value
        ), f"Expected '{type(value).__name__}:{value}' got '{type(v).__name__}:{v}'"


@then("the result is")
def step_impl(context):
    for row in context.table:
        _assert_value(context.result, row["path"].split("."), parse_value(row["value"]))


@then("the result is {a:An} {type_name:String} with")
def step_impl(context: Context, a, type_name):
    assert context.result, f"Expected result got error {context.error}"
    value = context.result
    value_type = type(value).__name__
    assert value_type == type_name, f"Expected type '{type_name}' got '{value_type}'"
    for row in context.table:
        property_name = row["property"]
        expected_value = row["value"]
        actual_value = read_value_from_path(value, property_name)
        if isinstance(actual_value, UUID):
            actual_value = str(actual_value)
        assert_equal(actual_value, expected_value)


@then("the result {path:Path} is {a:An} {type_name:String} with")
def step_impl(context, path, a, type_name):
    assert context.result, "Expected result"
    value = read_value_from_path(context.result, path)
    assert value, f"Value not present: {path}"
    value_type = type(value).__name__
    assert value_type == type_name, f"Expected type '{type_name}' got '{value_type}'"
    for row in context.table:
        property_name = row["property"]
        expected_value = parse_value(row["value"])
        actual_value = read_value_from_path(value, property_name)
        assert (
            actual_value == expected_value
        ), f"Expected value '{expected_value}' got '{actual_value}'"
