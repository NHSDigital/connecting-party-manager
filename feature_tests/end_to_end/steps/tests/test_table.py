import pytest

from feature_tests.end_to_end.steps.assertion import assert_is_subset
from feature_tests.end_to_end.steps.table import _unpack_nested_lists


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "one0": {
                    "one1": "123 ${ dollar() } abc",
                },
                "two0": "123 ${ uuid(1) } abc",
            },
            {
                "one0": {
                    "one1": "123 $ abc",
                },
                "two0": "123 ae2ab026-0b53-7e7c-7a65-f0407a6e75f5 abc",
            },
        )
    ],
)
def test__unpack_nested_lists(data, expected):
    result = _unpack_nested_lists(data)
    assert_is_subset(result, expected)
    assert_is_subset(expected, result)
