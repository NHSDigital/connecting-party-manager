from http import HTTPStatus

from domain.fhir.r4 import (
    CodeableConcept,
    Meta,
    OperationOutcome,
    OperationOutcomeIssue,
    ProfileItem,
)

from .coding import CODE_SYSTEM, CpmCoding, IssueSeverity, IssueType
from .response_matrix import coding_from_http_status

META = Meta(profile=[ProfileItem(__root__=CODE_SYSTEM)])


def _operation_outcome(
    id: str,
    coding: CpmCoding,
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


def operation_outcome_ok(id: str, http_status: HTTPStatus) -> dict:
    coding = coding_from_http_status(http_status=http_status)
    operation_outcome = _operation_outcome(
        id=id,
        coding=coding,
        diagnostics=coding._value_.display,
        issue_type=IssueType.INFORMATIONAL,
        severity=IssueSeverity.INFORMATION,
    )
    return operation_outcome
