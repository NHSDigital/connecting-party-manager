from domain.response.coding import IssueSeverity, IssueType
from domain.response.operation_outcome import _operation_outcome
from domain.response.response_matrix import CpmCoding
from hypothesis import given
from hypothesis.strategies import builds, just


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
    _possible_codings = [item.value for item in CpmCoding]
    assert _coding in _possible_codings
