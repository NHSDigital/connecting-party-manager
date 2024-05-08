from http import HTTPStatus

from api_utils.versioning.errors import VersionException
from domain.ods import InvalidOdsCodeError
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from event.status.steps import StatusNotOk

from .coding import CpmCoding, FhirCoding
from .validation_errors import (
    InboundJSONDecodeError,
    InboundMissingValue,
    InboundQueryValidationError,
    InboundValidationError,
)

HTTP_STATUS_TO_CPM_CODING = {
    # Success matrix here
    HTTPStatus.OK: CpmCoding.OK,
    HTTPStatus.CREATED: CpmCoding.RESOURCE_CREATED,
}

FHIR_CODING_TO_HTTP_STATUS = {
    # Part 1 of the error matrix here:
    # 400
    FhirCoding.MISSING_VALUE: HTTPStatus.BAD_REQUEST,
    FhirCoding.VALIDATION_ERROR: HTTPStatus.BAD_REQUEST,
    # 403
    FhirCoding.ACCESS_DENIED: HTTPStatus.FORBIDDEN,
    # 404
    FhirCoding.RESOURCE_NOT_FOUND: HTTPStatus.NOT_FOUND,
    # 422
    FhirCoding.UNPROCESSABLE_ENTITY: HTTPStatus.UNPROCESSABLE_ENTITY,
    # 500
    FhirCoding.SERVICE_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    # 503
    FhirCoding.SERVICE_UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
}

EXCEPTIONS_TO_FHIR_CODING = {
    # Part 2 of the error matrix here
    InboundValidationError: FhirCoding.VALIDATION_ERROR,
    InboundMissingValue: FhirCoding.MISSING_VALUE,
    InboundJSONDecodeError: FhirCoding.VALIDATION_ERROR,
    InvalidOdsCodeError: FhirCoding.UNPROCESSABLE_ENTITY,
    VersionException: FhirCoding.ACCESS_DENIED,
    AlreadyExistsError: FhirCoding.VALIDATION_ERROR,
    ItemNotFound: FhirCoding.RESOURCE_NOT_FOUND,
    StatusNotOk: FhirCoding.SERVICE_UNAVAILABLE,
    InboundQueryValidationError: FhirCoding.VALIDATION_ERROR,
}

SUCCESS_STATUSES = set(HTTP_STATUS_TO_CPM_CODING)
EXPECTED_EXCEPTIONS = tuple(EXCEPTIONS_TO_FHIR_CODING)
