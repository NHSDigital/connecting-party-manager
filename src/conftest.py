import json

from event.logging.logger import setup_logger
from nhs_context_logging.fixtures import log_capture, log_capture_global  # noqa: F401
from nhs_context_logging.formatters import json_serializer
from pytest import FixtureRequest, fixture


def pytest_collection_modifyitems(items, config):
    # add `unit` marker to all unmarked items
    for item in items:
        if not any(item.iter_markers()):
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
