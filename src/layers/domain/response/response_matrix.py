from http import HTTPStatus

from api_utils.versioning.errors import VersionException
from domain.ods import InvalidOdsCodeError
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from event.status.steps import StatusNotOk

from .coding import CpmCoding, SpineCoding
from .validation_errors import (
    InboundJSONDecodeError,
    InboundMissingValue,
    InboundValidationError,
)

HTTP_STATUS_TO_CPM_CODING = {
    # Success matrix here
    HTTPStatus.OK: CpmCoding.OK,
    HTTPStatus.CREATED: CpmCoding.RESOURCE_CREATED,
}

SPINE_CODING_TO_HTTP_STATUS = {
    # Part 1 of the error matrix here:
    # 400
    SpineCoding.MISSING_VALUE: HTTPStatus.BAD_REQUEST,
    SpineCoding.VALIDATION_ERROR: HTTPStatus.BAD_REQUEST,
    # 403
    SpineCoding.ACCESS_DENIED: HTTPStatus.FORBIDDEN,
    # 404
    SpineCoding.RESOURCE_NOT_FOUND: HTTPStatus.NOT_FOUND,
    # 422
    SpineCoding.UNPROCESSABLE_ENTITY: HTTPStatus.UNPROCESSABLE_ENTITY,
    # 500
    SpineCoding.SERVICE_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    # 503
    SpineCoding.SERVICE_UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
}

EXCEPTIONS_TO_SPINE_CODING = {
    # Part 2 of the error matrix here
    InboundValidationError: SpineCoding.VALIDATION_ERROR,
    InboundMissingValue: SpineCoding.MISSING_VALUE,
    InboundJSONDecodeError: SpineCoding.VALIDATION_ERROR,
    InvalidOdsCodeError: SpineCoding.UNPROCESSABLE_ENTITY,
    VersionException: SpineCoding.ACCESS_DENIED,
    AlreadyExistsError: SpineCoding.VALIDATION_ERROR,
    ItemNotFound: SpineCoding.RESOURCE_NOT_FOUND,
    StatusNotOk: SpineCoding.SERVICE_UNAVAILABLE,
}

SUCCESS_STATUSES = {*HTTP_STATUS_TO_CPM_CODING.keys(), HTTPStatus.NO_CONTENT}
EXPECTED_EXCEPTIONS = tuple(EXCEPTIONS_TO_SPINE_CODING)


def http_status_from_coding(coding: SpineCoding) -> HTTPStatus:
    return SPINE_CODING_TO_HTTP_STATUS[coding]


def http_status_from_exception(exception: Exception) -> HTTPStatus:
    coding = spine_coding_from_exception(exception=exception)
    return http_status_from_coding(coding=coding)


def coding_from_http_status(http_status: HTTPStatus) -> CpmCoding:
    return HTTP_STATUS_TO_CPM_CODING[http_status]


def spine_coding_from_exception(
    exception: Exception | type[Exception],
) -> SpineCoding:
    exception_type = (
        exception.__class__ if isinstance(exception, Exception) else exception
    )
    return EXCEPTIONS_TO_SPINE_CODING.get(exception_type, SpineCoding.SERVICE_ERROR)
