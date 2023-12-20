import json

from event.aws.client import dynamodb_client
from event.logging.logger import setup_logger
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_fixture as log_capture,
)
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_global_fixture as log_capture_global,
)
from nhs_context_logging.formatters import json_serializer
from pytest import Config, FixtureRequest, Item, fixture

from test_helpers.aws_session import aws_session
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def is_integration(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("integration") is not None


def pytest_collection_modifyitems(items: list[Item], config: Config):
    """Add 'unit' marker to unmarked tests"""
    custom_markers = config._getini(("markers"))
    hypothesis_marker_idx = custom_markers.index(
        "hypothesis: Tests which use hypothesis."
    )
    custom_markers = custom_markers[:hypothesis_marker_idx]
    for item in items:
        unmarked_test = True
        for marker in item.iter_markers():
            if marker.name in custom_markers:
                unmarked_test = False
                break
        if unmarked_test:
            item.add_marker("unit")


@fixture(autouse=True)
def log_on_failure(request: FixtureRequest, log_capture):
    setup_logger(request.node.name)

    exception = None
    try:
        yield
    except Exception as exception:
        pass

    std_out, std_err = log_capture
    for log in (*std_out, *std_err):
        print(json.dumps(log, indent=2, default=json_serializer))  # noqa: T201

    if isinstance(exception, Exception):
        raise exception


@fixture(autouse=True)
def aws_session_(request: FixtureRequest):
    if is_integration(request):
        with aws_session():
            yield
    else:
        yield


@fixture(autouse=True)
def clear_dynamodb_table_(request: FixtureRequest):
    client, table_name = None, None
    if is_integration(request):
        client = dynamodb_client()
        table_name = read_terraform_output("dynamodb_table_name.value")
        clear_dynamodb_table(client=client, table_name=table_name)
        yield
    else:
        yield
