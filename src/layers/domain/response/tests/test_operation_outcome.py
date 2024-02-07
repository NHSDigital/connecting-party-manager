from domain.response.coding import IssueSeverity, IssueType
from domain.response.operation_outcome import (
    _operation_outcome,
    _operation_outcome_from_validation_error,
)
from domain.response.response_matrix import CpmCoding, FhirCoding
from domain.response.validation_errors import ValidationErrorItem
from hypothesis import given
from hypothesis.strategies import builds, just, lists, sampled_from


@given(
    operation_outcome=builds(
        _operation_outcome, id=just("id_123"), diagnostics=just("an error message")
    )
)
def test__operation_outcome(operation_outcome: dict):
    assert operation_outcome["resourceType"] == "OperationOutcome"
    assert operation_outcome["id"] == "id_123"
    assert operation_outcome["meta"] == {
        "profile": [
            "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
        ]
    }

    (issue,) = operation_outcome["issue"]
    assert issue["diagnostics"] == "an error message"
    assert issue["severity"] in IssueSeverity._value2member_map_
    assert issue["code"] in IssueType._value2member_map_

    (_coding,) = issue["details"]["coding"]
    _possible_codings = (
        *[item.value for item in CpmCoding],
        *[item.value for item in FhirCoding],
    )
    assert _coding in _possible_codings


@given(
    operation_outcome=builds(
        _operation_outcome_from_validation_error,
        id=just("id_123"),
        error_items=lists(
            builds(
                ValidationErrorItem,
                type=sampled_from(
                    (
                        "value_error.missing",
                        "other",
                    )
                ),
                msg=just("all_good"),
                model_name=just("my_model"),
                loc=just(("path",)),
            )
        ),
    )
)
def test__operation_outcome_from_validation_error(operation_outcome: dict):
    assert operation_outcome["resourceType"] == "OperationOutcome"
    assert operation_outcome["id"] == "id_123"
    assert operation_outcome["meta"] == {
        "profile": [
            "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
        ]
    }

    for issue in operation_outcome["issue"]:
        assert issue["diagnostics"] == "all_good"
        assert issue["severity"] == IssueSeverity.ERROR
        assert issue["code"] == IssueType.PROCESSING

        (_coding,) = issue["details"]["coding"]
        _possible_codings = [item.value for item in FhirCoding]
        assert _coding in _possible_codings
