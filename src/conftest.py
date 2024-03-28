import json
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
from pytest import Config, FixtureRequest, Item, fixture

from test_helpers.aws_session import aws_session
from test_helpers.constants import PROJECT_ROOT
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output


def is_integration(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("integration") is not None


def is_smoke(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("smoke") is not None


def is_s3(request: FixtureRequest) -> bool:
    return request.node.get_closest_marker("s3") is not None


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
    if is_integration(request) or is_smoke(request):
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
