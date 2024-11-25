from sds.cpm_translation.utils import (
    _cross_product,
    _sds_metadata_to_device_tags,
    get_in_list_of_dict,
    update_in_list_of_dict,
)


def test_update_in_list_of_dict():
    obj = [{"foo": "FOO", "hello": "world"}, {"foo": "OOF"}]
    update_in_list_of_dict(obj=obj, key="foo", value="bar")
    assert obj == [{"foo": "bar", "hello": "world"}, {"foo": "bar"}]


def test_update_in_list_of_dict_doesnt_exist():
    obj = [{"hello": "world"}]
    update_in_list_of_dict(obj=obj, key="foo", value="bar")
    assert obj == [{"hello": "world"}, {"foo": "bar"}]


def test_update_in_list_of_dict_deletes_if_falsey():
    obj = [{"foo": "FOO", "hello": "world"}, {"foo": "OOF"}]
    update_in_list_of_dict(obj=obj, key="foo", value=[])
    assert obj == [{"hello": "world"}]


def test_update_in_list_of_dict_deletes_if_falsey_doesnt_exist():
    obj = [{"hello": "world"}]
    update_in_list_of_dict(obj=obj, key="foo", value=[])
    assert obj == [{"hello": "world"}]


def test_get_in_list_of_dict():
    obj = [{"foo": "FOO", "hello": "world"}, {"foo": "OOF"}]
    assert get_in_list_of_dict(obj=obj, key="foo") == "FOO"
    assert get_in_list_of_dict(obj=obj, key="hello") == "world"
    assert get_in_list_of_dict(obj=obj, key="bar") is None


def test_cross_product():
    matrix = [
        [{"foo": "bar"}, {"foo": "bob"}, {"foo": "boo"}],
        [{"bar": "bar"}, {"bar": "bob"}, {"bar": "boo"}],
        [{"bob": "bar"}, {"bob": "bob"}, {"bob": "boo"}],
        [{"baz": "bar"}, {"baz": "bob"}, {"baz": "boo"}],
        [{"boo": "bar"}, {"boo": "bob"}, {"boo": "boo"}],
        [{"oops": "bar"}, {"oops": "bob"}, {"oops": "boo"}],
        [{"mmm": "bar"}, {"mmm": "bob"}, {"mmm": "boo"}],
        [{"abc": "bar"}, {"abc": "bob"}, {"abc": "boo"}],
        [{"xyz": "bar"}, {"xyz": "bob"}, {"xyz": "boo"}],
    ]
    vectors = _cross_product(matrix)
    assert len(vectors) == 19683


def sorted_dicts(items: list[dict]):
    return sorted(
        ({k: item[k] for k in sorted(item.keys())} for item in items),
        key=lambda item: tuple(item.items()),
    )


def test_sds_metadata_to_device_tags():
    data = {
        "me": ["you"],
        "0": ("0", "0"),
        "1": {"1", "1"},
        "2": ["2", "2"],
        "her": "him",
        "foo": ["bar"],
        "boo": {"bam", "bop", "bloop"},
        "baz": ("mmm", "abc"),
    }

    for _ in range(10000):
        tags = _sds_metadata_to_device_tags(
            data=data,
            tag_fields=["foo", "boo", "baz", "me", "her"],
        )

        assert sorted_dicts(tags) == sorted_dicts(
            [
                {"baz": "mmm", "boo": "bam", "foo": "bar", "her": "him", "me": "you"},
                {"baz": "abc", "boo": "bam", "foo": "bar", "her": "him", "me": "you"},
                {"baz": "mmm", "boo": "bop", "foo": "bar", "her": "him", "me": "you"},
                {"baz": "abc", "boo": "bop", "foo": "bar", "her": "him", "me": "you"},
                {"baz": "mmm", "boo": "bloop", "foo": "bar", "her": "him", "me": "you"},
                {"baz": "abc", "boo": "bloop", "foo": "bar", "her": "him", "me": "you"},
            ]
        )


def test_sds_metadata_to_device_tags_empty():
    data = {
        "me": ["you"],
        "0": ("0", "0"),
        "1": {"1", "1"},
        "2": ["2", "2"],
        "her": "him",
        "foo": ["bar"],
        "boo": {"bam", "bop", "bloop"},
        "baz": ("mmm", "abc"),
    }

    tags = _sds_metadata_to_device_tags(
        data=data, tag_fields=["something that isn't there"]
    )
    assert tags == []
