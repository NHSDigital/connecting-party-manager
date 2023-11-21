from string import ascii_letters

from event.response.coding import IssueSeverity, IssueType
from event.response.operation_outcome import (
    _operation_outcome,
    _operation_outcome_from_validation_error,
)
from event.response.response_matrix import CpmCoding, FhirCoding
from hypothesis import given
from hypothesis.strategies import builds, dictionaries, just, text


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
        path_error_mapping=dictionaries(
            keys=text(min_size=1, alphabet=ascii_letters),
            values=text(min_size=1, alphabet=ascii_letters),
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
        assert type(issue["diagnostics"]) is str
        assert issue["severity"] == IssueSeverity.ERROR
        assert issue["code"] == IssueType.PROCESSING

        (_coding,) = issue["details"]["coding"]
        _possible_codings = [item.value for item in FhirCoding]
        assert _coding in _possible_codings
