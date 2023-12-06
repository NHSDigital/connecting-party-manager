from uuid import uuid4

import pytest
from domain.repository.keys import (
    TableKeys,
    group_by_key,
    remove_keys,
    strip_key_prefix,
)

FIXED_UUID = uuid4()


@pytest.mark.parametrize(
    ("table_key", "args", "expected"),
    [
        (TableKeys.DEVICE, (FIXED_UUID, "foo", 1), f"D#{FIXED_UUID}#foo#1"),
        (TableKeys.PRODUCT_TEAM, ("foo",), "PT#foo"),
    ],
)
def test_TableKeys_key(table_key: TableKeys, args, expected):
    assert table_key.key(*args) == expected


@pytest.mark.parametrize(
    ("table_key", "expected"),
    [
        (TableKeys.DEVICE, [{"key": "D#foo"}, {"key": "D#bar"}]),
        (TableKeys.PRODUCT_TEAM, [{"key": "PT#foo"}]),
    ],
)
def test_TableKeys_filter(table_key: TableKeys, expected):
    iterable = [{"key": "D#foo"}, {"key": "PT#foo"}, {"key": "D#bar"}]
    assert list(table_key.filter(iterable=iterable, key="key")) == expected


@pytest.mark.parametrize(
    ("table_key", "expected"),
    [
        (
            TableKeys.DEVICE,
            [("foo", {"other_data": "FOO"}), ("bar", {"other_data": "BAR"})],
        ),
        (
            TableKeys.PRODUCT_TEAM,
            [("baz", {"other_data": "BAZ"})],
        ),
    ],
)
def test_TableKeys_filter_and_group(table_key: TableKeys, expected):
    iterable = [
        {"pk_1": "D#foo", "other_data": "FOO"},
        {"pk_1": "PT#baz", "other_data": "BAZ"},
        {"pk_1": "D#bar", "other_data": "BAR"},
    ]
    assert list(table_key.filter_and_group(iterable=iterable, key="pk_1")) == expected


def test_group_by_key():
    iterable = [
        {"pk_1": "D#foo", "other_data": "FOO"},
        {"pk_1": "PT#baz", "other_data": "BAZ"},
        {"pk_1": "D#bar", "other_data": "BAR"},
    ]
    assert list(group_by_key(iterable=iterable, key="pk_1")) == [
        ("foo", {"other_data": "FOO"}),
        ("baz", {"other_data": "BAZ"}),
        ("bar", {"other_data": "BAR"}),
    ]


def test_strip_key_prefix():
    strip_key_prefix("P#123#456") == "123#456"


def test_remove_keys():
    result = remove_keys(
        **{
            "pk": "0",
            "sk": "0",
            "pk_1": "1",
            "sk_1": "1",
            "pk_2": "2",
            "sk_2": "2",
            "pk_3": "3",
            "sk_3": "3",
            "foo": "FOO",
            "pk_4": "4",
            "bar": "BAR",
            "sk_4": "4",
            "pk_5": "5",
            "sk_5": "5",
            "baz": "BAZ",
        }
    )
    assert result == {
        "foo": "FOO",
        "bar": "BAR",
        "baz": "BAZ",
    }
