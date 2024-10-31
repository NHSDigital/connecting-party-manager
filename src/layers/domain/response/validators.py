import json
from http import HTTPStatus

from .response_matrix import SUCCESS_STATUSES


class UnexpectedHttpStatus(Exception):
    def __init__(self, http_status):
        super().__init__(
            f"HTTP Status '{http_status}' should not be "
            "explicitly returned from the API. For non-2XX "
            "statuses we should raise exceptions for "
            "control flow of API failures. Any 2XX statuses "
            "should be added to SUCCESS_STATUSES."
        )


class NotJsonSerialisable(Exception):
    pass


class InvalidExceptionRaised(Exception):
    def __init__(self, exception):
        super().__init__(
            f"An exception of type '{exception.__class__.__name__}' was raised with no message"
        )


def validate_http_status_response(http_status: HTTPStatus):
    if http_status not in SUCCESS_STATUSES:
        raise UnexpectedHttpStatus(http_status=http_status)


def validate_json_serialisable_response(item):
    try:
        json.dumps(item)
    except Exception as exception:
        raise NotJsonSerialisable(str(exception))


def validate_exception(exception):
    if not str(exception):
        return InvalidExceptionRaised(exception)
    return exception
