import pytest
from event.logging.log_reference import make_log_reference


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        ("This is a Test!@#123", "THIS-IS-A-TEST-123"),
        ("ONLYUPPERCASELETTERS", "ONLYUPPERCASELETTERS"),
        ("onlylowercaseletters", "ONLYLOWERCASELETTERS"),
    ],
)
def test_make_log_reference(input_name, expected_output):
    assert make_log_reference(input_name) == expected_output
