from http import HTTPStatus

from domain.fhir.r4 import (
    CodeableConcept,
    Meta,
    OperationOutcome,
    OperationOutcomeIssue,
    ProfileItem,
)
from event.response.validation_errors import ValidationErrorItem, parse_validation_error
from pydantic import ValidationError

from .coding import CODE_SYSTEM, CpmCoding, FhirCoding, IssueSeverity, IssueType
from .response_matrix import (
    EXCEPTIONS_TO_FHIR_CODING,
    FHIR_CODING_TO_HTTP_STATUS,
    HTTP_STATUS_TO_CPM_CODING,
)

META = Meta(profile=[ProfileItem(__root__=CODE_SYSTEM)])


def _operation_outcome(
    id: str,
    coding: FhirCoding | CpmCoding,
    diagnostics: str,
    issue_type: IssueType = IssueType.PROCESSING,
    severity: IssueSeverity = IssueSeverity.ERROR,
) -> dict:
    issue_details = CodeableConcept(coding=[coding.value])
    issue = [
        OperationOutcomeIssue(
            code=issue_type.value,
            severity=severity.value,
            diagnostics=diagnostics,
            details=issue_details,
        )
    ]
    return OperationOutcome(
        resourceType=OperationOutcome.__name__, id=id, meta=META, issue=issue
    ).dict(exclude_none=True)


def _operation_outcome_from_validation_error(
    id: str, error_items: list[ValidationErrorItem]
) -> OperationOutcome:
    issue = [
        OperationOutcomeIssue(
            code=IssueType.PROCESSING.value,
            severity=IssueSeverity.ERROR.value,
            diagnostics=error_item.msg,
            details=CodeableConcept(
                coding=[_fhir_coding_from_exception(error_item.exception_type).value]
            ),
            expression=[error_item.path],
        )
        for error_item in error_items
    ]
    return OperationOutcome(
        resourceType=OperationOutcome.__name__, id=id, meta=META, issue=issue
    ).dict(exclude_none=True)


def _fhir_coding_from_exception(
    exception: Exception | type[Exception],
) -> FhirCoding:
    exception_type = (
        exception.__class__ if isinstance(exception, Exception) else exception
    )
    return EXCEPTIONS_TO_FHIR_CODING.get(exception_type, FhirCoding.SERVICE_ERROR)


def _http_status_from_coding(coding: FhirCoding) -> HTTPStatus:
    return FHIR_CODING_TO_HTTP_STATUS[coding]


def _coding_from_http_status(http_status: HTTPStatus) -> CpmCoding:
    return HTTP_STATUS_TO_CPM_CODING[http_status]


def operation_outcome_not_ok(id: str, exception: Exception) -> tuple[int, dict]:
    coding = _fhir_coding_from_exception(exception=exception)
    http_status = _http_status_from_coding(coding=coding)

    if isinstance(exception, ValidationError):
        error_items = parse_validation_error(validation_error=exception)
        operation_outcome = _operation_outcome_from_validation_error(
            id=id, error_items=error_items
        )
    else:
        operation_outcome = _operation_outcome(
            id=id, coding=coding, diagnostics=str(exception)
        )
    return http_status, operation_outcome


def operation_outcome_ok(id: str, http_status: HTTPStatus) -> dict:
    coding = _coding_from_http_status(http_status=http_status)
    operation_outcome = _operation_outcome(
        id=id,
        coding=coding,
        diagnostics=coding._value_.display,
        issue_type=IssueType.INFORMATIONAL,
        severity=IssueSeverity.INFORMATION,
    )
    return operation_outcome
