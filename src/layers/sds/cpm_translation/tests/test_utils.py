from sds.cpm_translation.utils import get_in_list_of_dict, update_in_list_of_dict


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
