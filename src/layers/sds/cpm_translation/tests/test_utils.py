from sds.cpm_translation.utils import (
    get_in_list_of_dict,
    questionnaire_response_answers_to_device_tags,
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


def test_questionnaire_response_answers_to_device_tags():
    tags = questionnaire_response_answers_to_device_tags(
        answers=[
            {"skip me": ["skip me"]},
            {"foo": ["bar"]},
            {"skip me": ["skip me"]},
            {"boo": ["bam", "bop"]},
            {"skip me": ["skip me"]},
            {"skip me": ["skip me"]},
        ],
        tag_fields=["foo", "boo"],
    )
    assert tags == [
        {"foo": "bar", "boo": "bam"},
        {"foo": "bar", "boo": "bop"},
    ]


def test_questionnaire_response_answers_to_device_tags_empty():
    tags = questionnaire_response_answers_to_device_tags(
        answers=[
            {"skip me": ["skip me"]},
            {"foo": ["bar"]},
            {"skip me": ["skip me"]},
            {"boo": ["bam", "bop"]},
            {"skip me": ["skip me"]},
            {"skip me": ["skip me"]},
        ],
        tag_fields=["something that isn't there"],
    )
    assert tags == []
