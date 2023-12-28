import json

from behave import given, then, when
from requests import JSONDecodeError

from feature_tests.end_to_end.steps.assertion import (
    assert_equal,
    assert_is_subset,
    assert_many,
    assert_same_type,
)
from feature_tests.end_to_end.steps.context import Context
from feature_tests.end_to_end.steps.postman import Body, HeaderItem, PostmanRequest, Url
from feature_tests.end_to_end.steps.requests import make_request
from feature_tests.end_to_end.steps.table import parse_table


def fix_backslashes(json_data):
    if "issue" in json_data and isinstance(json_data["issue"], list):
        for issue in json_data["issue"]:
            if "diagnostics" in issue and isinstance(issue["diagnostics"], str):
                issue["diagnostics"] = issue["diagnostics"].replace("\\\\", "\\")


def remove_ignore_keys(data1, data2):
    if isinstance(data1, dict) and isinstance(data2, dict):
        for key in list(data1.keys()):
            if data1[key] == "<< ignore >>":
                del data1[key]
                del data2[key]  # Synchronize removal in both dictionaries
            else:
                remove_ignore_keys(data1[key], data2[key])
    elif isinstance(data1, list) and isinstance(data2, list):
        for item1, item2 in zip(data1, data2):
            remove_ignore_keys(item1, item2)


@given('"{header_name}" request headers')
def given_request_headers(context: Context, header_name: str):
    context.headers[header_name] = parse_table(table=context.table)


@given(
    'I have already made a "{http_method}" request with "{header_name}" headers to "{endpoint}" with body'
)
def given_made_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    body = parse_table(table=context.table)
    response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        body=body,
        raise_for_status=True,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(raw=response.url, host=[context.base_url.rstrip("/")], path=[endpoint]),
        method=http_method,
        header=[
            HeaderItem(key=k, value=v) for k, v in context.headers[header_name].items()
        ],
        body=Body(raw=json.dumps(body) if isinstance(body, dict) else body),
    )


@given(
    'I have already made a "{http_method}" request with "{header_name}" headers to "{endpoint}"'
)
def given_made_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        raise_for_status=True,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(raw=response.url, host=[context.base_url.rstrip("/")], path=[endpoint]),
        method=http_method,
        header=[
            HeaderItem(key=k, value=v) for k, v in context.headers[header_name].items()
        ],
    )


@when(
    'I make a "{http_method}" request with "{header_name}" headers to "{endpoint}" with body'
)
def when_make_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    body = parse_table(table=context.table) if context.table else context.text
    context.response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        body=body,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(
            raw=context.response.url,
            host=[context.base_url.rstrip("/")],
            path=[endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value=v) for k, v in context.headers[header_name].items()
        ],
        body=Body(raw=json.dumps(body) if isinstance(body, dict) else body),
    )


@when('I make a "{http_method}" request with "{header_name}" headers to "{endpoint}"')
def when_make_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    context.response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
    )
    context.postman_step.request = PostmanRequest(
        url=Url(
            raw=context.response.url,
            host=[context.base_url.rstrip("/")],
            path=[endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value=v) for k, v in context.headers[header_name].items()
        ],
    )


@then('I receive a status code "{status_code}" with body')
def then_response(context: Context, status_code: str):
    expected_body = parse_table(table=context.table)
    try:
        response_body = context.response.json()
    except JSONDecodeError:
        response_body = context.response.text
    fix_backslashes(expected_body)
    remove_ignore_keys(expected_body, response_body)
    assert_many(
        assertions=(
            assert_equal,
            assert_same_type,
            assert_equal,
            assert_is_subset,
            assert_is_subset,
        ),
        expected=(
            int(status_code),
            expected_body,
            expected_body,
            expected_body,
            response_body,
        ),
        received=(
            context.response.status_code,
            response_body,
            response_body,
            response_body,
            expected_body,
        ),
    )


@then('I receive a status code "{status_code}"')
def then_response(context: Context, status_code: str):
    assert_equal(
        expected=int(status_code),
        received=context.response.status_code,
    )


@then("the response headers contain")
def then_response(context: Context):
    expected_response_headers = parse_table(table=context.table)
    assert_is_subset(
        expected=expected_response_headers, received=context.response.headers
    )
