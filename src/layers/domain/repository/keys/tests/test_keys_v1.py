from uuid import uuid4

import pytest
from domain.repository.keys import TableKey, group_by_key, remove_keys, strip_key_prefix

FIXED_UUID = uuid4()


@pytest.mark.parametrize(
    ("table_key", "args", "expected"),
    [
        (TableKey.PRODUCT_TEAM, ("foo",), "PT#foo"),
    ],
)
def test_TableKeys_key(table_key: TableKey, args, expected):
    assert table_key.key(*args) == expected


@pytest.mark.parametrize(
    ("table_key", "expected"),
    [
        (TableKey.CPM_PRODUCT, [{"key": "P#foo"}, {"key": "P#bar"}]),
        (TableKey.PRODUCT_TEAM, [{"key": "PT#foo"}]),
    ],
)
def test_TableKeys_filter(table_key: TableKey, expected):
    iterable = [{"key": "P#foo"}, {"key": "PT#foo"}, {"key": "P#bar"}]
    assert list(table_key.filter(iterable=iterable, key="key")) == expected


@pytest.mark.parametrize(
    ("table_key", "expected"),
    [
        (
            TableKey.CPM_PRODUCT,
            [("foo", {"other_data": "FOO"}), ("bar", {"other_data": "BAR"})],
        ),
        (
            TableKey.PRODUCT_TEAM,
            [("baz", {"other_data": "BAZ"})],
        ),
    ],
)
def test_TableKeys_filter_and_group(table_key: TableKey, expected):
    iterable = [
        {"pk": "P#foo", "other_data": "FOO"},
        {"pk": "PT#baz", "other_data": "BAZ"},
        {"pk": "P#bar", "other_data": "BAR"},
    ]
    assert list(table_key.filter_and_group(iterable=iterable, key="pk")) == expected


def test_group_by_key():
    iterable = [
        {"pk_read": "P#foo", "other_data": "FOO"},
        {"pk_read": "PT#baz", "other_data": "BAZ"},
        {"pk_read": "P#bar", "other_data": "BAR"},
    ]
    assert list(group_by_key(iterable=iterable, key="pk_read")) == [
        ("foo", {"other_data": "FOO"}),
        ("baz", {"other_data": "BAZ"}),
        ("bar", {"other_data": "BAR"}),
    ]


def test_strip_key_prefix():
    result = strip_key_prefix("P#123#456")
    expected = "123#456"
    assert result == expected


def test_remove_keys():
    result = remove_keys(
        **{
            "pk": "0",
            "sk": "0",
            "pk_read": "1",
            "sk_read": "1",
            "foo": "FOO",
            "bar": "BAR",
            "baz": "BAZ",
        }
    )
    assert result == {
        "foo": "FOO",
        "bar": "BAR",
        "baz": "BAZ",
    }
