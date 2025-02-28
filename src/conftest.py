import json
import time
from pathlib import Path

import boto3
from event.aws.client import dynamodb_client
from event.logging.logger import setup_logger
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_fixture as log_capture,
)
from nhs_context_logging.fixtures import (  # noqa: F401
    log_capture_global_fixture as log_capture_global,
)
from nhs_context_logging.formatters import json_serializer
from pytest import Config, FixtureRequest, Item, Parser, fixture

from test_helpers.aws_session import aws_session
from test_helpers.constants import PROJECT_ROOT
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def pytest_addoption(parser: Parser):
    parser.addoption("--suppress-logs", action="store", default=False)


def is_integration(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("integration") is not None


def is_smoke(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("smoke") is not None


def is_s3(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("s3") is not None


def is_matrix(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("matrix") is not None


def dynamodb_client_with_sleep():
    """
    Since we use GSIs we need to give time for the GSI-projections time
    to sync with the root table. We have implemented sleeps:

    * after 'write' operations.
    * before 'query' operations.
    """
    client = dynamodb_client()
    unpatched_transact_write_items = client.transact_write_items
    unpatched_query = client.query

    def _transact_write_items_with_sleep(*args, **kwargs):
        response = unpatched_transact_write_items(*args, **kwargs)
        time.sleep(0.5)
        return response

    def _query_with_sleep(*args, **kwargs):
        time.sleep(0.2)
        response = unpatched_query(*args, **kwargs)
        return response

    client.transact_write_items = _transact_write_items_with_sleep
    client.query = _query_with_sleep
    return client


def download_files_from_s3(request: FixtureRequest):
    client = boto3.client("s3")
    test_data_bucket = read_terraform_output("test_data_bucket.value")
    s3_paths = []
    for key in request.node.get_closest_marker("s3").args:
        download_path = PROJECT_ROOT / ".downloads" / Path(key)
        s3_paths.append(download_path)
        if download_path.exists():
            continue
        download_path.parent.mkdir(parents=True, exist_ok=True)
        client.download_file(
            Bucket=test_data_bucket, Key=key, Filename=str(download_path)
        )
    return s3_paths


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
def log_on_failure(pytestconfig: Config, request: FixtureRequest, log_capture):
    setup_logger(request.node.name)

    if pytestconfig.getoption("suppress_logs") is not False:
        from nhs_context_logging import app_logger

        app_logger.log = lambda *args, **kwargs: None

    exception = None
    try:
        yield
    except Exception as exception:
        pass

    std_out, std_err = log_capture
    for log in (*std_out, *std_err):
        if pytestconfig.getoption("suppress_logs") is False:
            serialised = json_serializer(log)
            print(json.dumps(serialised, indent=2))  # noqa: T201

    if isinstance(exception, Exception):
        raise exception


@fixture(autouse=True)
def aws_session_(request: FixtureRequest):
    if is_integration(request):
        with aws_session():
            yield
    elif is_smoke(request):
        with aws_session(role_name="NHSSmokeTestRole"):
            yield
    else:
        yield


@fixture(autouse=True)
def clear_dynamodb_table_(request: FixtureRequest):
    if is_integration(request):
        client = dynamodb_client()
        table_name_cpm = read_terraform_output("dynamodb_cpm_table_name.value")
        clear_dynamodb_table(client=client, table_name=table_name_cpm)
        yield
    else:
        yield


@fixture(autouse=True)
def test_data_paths(request: FixtureRequest):
    """
    Returns local paths to downloaded s3 files. This complements the marker

        'pytest.mark.s3("path/to/file/in/test_bucket", "path/to/other/file/in/test_bucket")'

    which this fixture hooks to via 'is_s3'
    """
    if is_s3(request):
        with aws_session():
            paths = download_files_from_s3(request)
        yield paths
    else:
        yield
