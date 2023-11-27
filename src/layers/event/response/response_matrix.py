from http import HTTPStatus

from event.versioning.errors import VersionException

from .coding import CpmCoding, FhirCoding
from .validation_errors import InboundValidationError

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
    # 422
    FhirCoding.UNPROCESSABLE_ENTITY: HTTPStatus.UNPROCESSABLE_ENTITY,
    # 500
    FhirCoding.SERVICE_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
}

EXCEPTIONS_TO_FHIR_CODING = {
    # Part 2 of the error matrix here
    InboundValidationError: FhirCoding.VALIDATION_ERROR,
    VersionException: FhirCoding.ACCESS_DENIED,
}

SUCCESS_STATUSES = set(HTTP_STATUS_TO_CPM_CODING)
EXPECTED_EXCEPTIONS = tuple(EXCEPTIONS_TO_FHIR_CODING)
