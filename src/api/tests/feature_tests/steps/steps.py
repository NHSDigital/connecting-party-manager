import json

from requests import JSONDecodeError

from api.tests.feature_tests.steps.assertion import (
    assert_equal,
    assert_is_subset,
    assert_many,
    assert_same_type,
)
from api.tests.feature_tests.steps.context import Context
from api.tests.feature_tests.steps.decorators import given, then, when
from api.tests.feature_tests.steps.postman import (
    Body,
    Event,
    HeaderItem,
    PostmanEnvironmentValue,
    PostmanRequest,
    Script,
    Url,
    jsonpath_to_javascript_path,
)
from api.tests.feature_tests.steps.requests import make_request
from api.tests.feature_tests.steps.table import (
    extract_from_response_by_jsonpath,
    parse_table,
)

sort_keys = {"product": "name"}


@given('"{header_name}" request headers')
def given_request_headers(context: Context, header_name: str):
    table_headers = parse_table(table=context.table, context=context)
    context.headers[header_name] = dict(**table_headers, apikey=context.api_key)


@given(
    'I have already made a "{http_method}" request with "{header_name}" headers to "{endpoint}" with body'
)
def given_made_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    body = parse_table(table=context.table, context=context)
    context.response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        body=body,
        raise_for_status=True,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(
            raw=context.base_url + context.postman_endpoint,
            host=[context.base_url.rstrip("/")],
            path=[context.postman_endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value="{{apiKey}}" if k == "apikey" else v)
            for k, v in context.headers[header_name].items()
        ],
        body=Body(raw=json.dumps(body) if isinstance(body, dict) else body),
    )


@given(
    'I have already made a "{http_method}" request with "{header_name}" headers to "{endpoint}"'
)
def given_made_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    context.response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        raise_for_status=True,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(
            raw=context.base_url + context.postman_endpoint,
            host=[context.base_url.rstrip("/")],
            path=[context.postman_endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value="{{apiKey}}" if k == "apikey" else v)
            for k, v in context.headers[header_name].items()
        ],
    )


@when(
    'I make a "{http_method}" request with "{header_name}" headers to "{endpoint}" with body'
)
def when_make_request(
    context: Context, http_method: str, header_name: str, endpoint: str
):
    body = (
        parse_table(table=context.table, context=context)
        if context.table
        else context.text
    )
    context.response = make_request(
        base_url=context.base_url,
        http_method=http_method,
        endpoint=endpoint,
        headers=context.headers[header_name],
        body=body,
    )
    context.postman_step.request = PostmanRequest(
        url=Url(
            raw=context.base_url + context.postman_endpoint,
            host=[context.base_url.rstrip("/")],
            path=[context.postman_endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value="{{apiKey}}" if k == "apikey" else v)
            for k, v in context.headers[header_name].items()
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
            raw=context.base_url + context.postman_endpoint,
            host=[context.base_url.rstrip("/")],
            path=[context.postman_endpoint],
        ),
        method=http_method,
        header=[
            HeaderItem(key=k, value="{{apiKey}}" if k == "apikey" else v)
            for k, v in context.headers[header_name].items()
        ],
    )


@then('I receive a status code "{status_code}" with body')
def then_response(context: Context, status_code: str):
    expected_body = parse_table(table=context.table, context=context)
    try:
        response_body = context.response.json()
    except JSONDecodeError:
        response_body = context.response.text
    assert_many(
        assertions=(
            assert_equal,
            assert_same_type,
            assert_equal,
        ),
        expected=(
            int(status_code),
            expected_body,
            expected_body,
        ),
        received=(
            context.response.status_code,
            response_body,
            response_body,
        ),
    )


@then(
    'I receive a status code "{status_code}" with body where "{list_to_check}" has a length of "{count}"'
)
def then_response(context: Context, status_code: str, list_to_check: str, count: str):
    expected_body = parse_table(table=context.table, context=context)
    try:
        response_body = context.response.json()
    except JSONDecodeError:
        response_body = context.response.text
    if list_to_check == "results":
        assert len(response_body["results"]) == int(count)
        expected_body[list_to_check] = sorted(
            expected_body[list_to_check], key=lambda x: x["name"]
        )
        response_body[list_to_check] = sorted(
            response_body[list_to_check], key=lambda x: x["name"]
        )

    assert_many(
        assertions=(
            assert_equal,
            assert_same_type,
            assert_equal,
        ),
        expected=(
            int(status_code),
            expected_body,
            expected_body,
        ),
        received=(
            context.response.status_code,
            response_body,
            response_body,
        ),
    )


@then(
    'I receive a status code "{status_code}" with body where ProductTeams has a length of "{product_team_count}" with "{product_count}" Products each'
)
def then_response(
    context: Context, status_code: str, product_team_count: str, product_count: str
):
    expected_body = parse_table(table=context.table, context=context)
    try:
        response_body = context.response.json()
    except JSONDecodeError:
        response_body = context.response.text

    len_product_teams = len(response_body["results"][0]["product_teams"])
    assert len_product_teams == int(product_team_count)

    len_products = 0
    for i in range(len_product_teams):
        len_products += len(response_body["results"][0]["product_teams"][i]["products"])
    assert len_products == int(product_count)

    # Sort product teams by "product_team_id"
    expected_body["results"][0]["product_teams"] = sorted(
        expected_body["results"][0]["product_teams"],
        key=lambda team: team["cpm_product_team_id"],
    )
    response_body["results"][0]["product_teams"] = sorted(
        response_body["results"][0]["product_teams"],
        key=lambda team: team["cpm_product_team_id"],
    )

    # Sort products inside each product team by "id"
    for i, _ in enumerate(expected_body["results"][0]["product_teams"]):
        expected_body["results"][0]["product_teams"][i]["products"] = sorted(
            expected_body["results"][0]["product_teams"][i]["products"],
            key=lambda product: product["id"],
        )
        response_body["results"][0]["product_teams"][i]["products"] = sorted(
            response_body["results"][0]["product_teams"][i]["products"],
            key=lambda product: product["id"],
        )

    assert_many(
        assertions=(
            assert_equal,
            assert_same_type,
            assert_equal,
        ),
        expected=(
            int(status_code),
            expected_body,
            expected_body,
        ),
        received=(
            context.response.status_code,
            response_body,
            response_body,
        ),
    )


@then('I receive a status code "{status_code}" with an empty body')
def then_response(context: Context, status_code: str):
    try:
        response_body = context.response.json()
    except JSONDecodeError:
        response_body = context.response.text
    assert response_body == []
    assert_equal(
        expected=int(status_code),
        received=context.response.status_code,
    )


@then('I receive a status code "{status_code}"')
def then_response(context: Context, status_code: str):
    assert_equal(
        expected=int(status_code),
        received=context.response.status_code,
    )


@then("the response headers contain")
def then_response(context: Context):
    expected_response_headers = parse_table(table=context.table, context=context)
    assert_is_subset(
        expected=expected_response_headers, received=context.response.headers
    )


for decorator in (given, when, then):

    @decorator('I note the response field "{jsonpath}" as "{alias}"')
    def note_response_field(context: Context, jsonpath: str, alias: str):
        context.notes[alias] = extract_from_response_by_jsonpath(
            response=context.response.json(), jsonpath=jsonpath
        )

        javascript_path = jsonpath_to_javascript_path(jsonpath)
        context.postman_scenario.item[-1].event.append(
            Event(
                script=Script(
                    exec=[
                        "if(pm.response.code >= 200 && pm.response.code < 300){",
                        f'    pm.environment.set("{alias}", pm.response.json(){javascript_path})',
                        "}",
                        "",
                    ]
                )
            )
        )
        if alias not in context.postman_environment:
            context.postman_environment.values.append(
                PostmanEnvironmentValue(key=alias, value="")
            )
