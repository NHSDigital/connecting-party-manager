import pytest
from sds.epr.tags.tags import (
    _generate_all_matching_queries,
    _valid_tag_exists,
    is_list_like,
)


@pytest.mark.parametrize(
    ["tag_fields", "data_fields", "result"],
    (
        [{"tag1"}, ["tag1", "tag2"], True],
        [{"tag1", "tag2"}, ["tag1", "tag2"], True],
        [{"tag1", "tag4"}, ["tag1", "tag2"], False],
    ),
)
def test_valid_tag_exists(tag_fields, data_fields, result):
    assert _valid_tag_exists(tag_fields=tag_fields, data_fields=data_fields) is result


@pytest.mark.parametrize(
    ["obj", "result"],
    [
        ([1, 2, 3], True),
        (tuple(), True),
        (set(), True),
        ("string", False),
        (123, False),
    ],
)
def test_is_list_like(obj, result):
    assert is_list_like(obj) is result


@pytest.mark.parametrize(
    ["data_to_query", "expected_output"],
    [
        (
            {
                "field1": "value1",
                "field2": ["value2a", "value2b"],
            },
            [
                (("field1", "value1"), ("field2", "value2a")),
                (("field1", "value1"), ("field2", "value2b")),
            ],
        ),
        (
            {
                "field1": ["value1a", "value1b"],
                "field2": ["value2a", "value2b"],
            },
            [
                (("field1", "value1a"), ("field2", "value2a")),
                (("field1", "value1a"), ("field2", "value2b")),
                (("field1", "value1b"), ("field2", "value2a")),
                (("field1", "value1b"), ("field2", "value2b")),
            ],
        ),
    ],
)
def test_generate_all_matching_queries(data_to_query, expected_output):
    assert _generate_all_matching_queries(data_to_query) == expected_output
