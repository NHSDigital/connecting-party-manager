import json
from datetime import datetime

import pytest
from domain.core.device import (
    Device,
    DeviceDeletedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceTag,
    DeviceTagAddedEvent,
    DeviceTagsAddedEvent,
    DeviceTagsClearedEvent,
    DeviceUpdatedEvent,
    DuplicateQuestionnaireResponse,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key import DeviceKey, DeviceKeyType
from domain.core.enum import Environment, Status
from domain.core.error import DuplicateError, NotFoundError
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.core.questionnaire.tests.test_questionnaire_v1 import VALID_SCHEMA


@pytest.fixture
def device():
    return Device(
        name="Foo",
        ods_code="ABC123",
        product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
        environment=Environment.DEV,
        product_id="P.XXX-YYY",
    )


@pytest.fixture
def questionnaire() -> Questionnaire:
    return Questionnaire(
        name="my-questionnaire", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )


@pytest.fixture
def questionnaire_response(questionnaire: Questionnaire) -> QuestionnaireResponse:
    questionnaire_response = questionnaire.validate({"size": 4, "colour": "white"})
    return questionnaire_response


@pytest.fixture
def another_good_questionnaire_response(
    questionnaire: Questionnaire,
) -> QuestionnaireResponse:
    questionnaire_response = questionnaire.validate({"size": 7, "colour": "black"})
    return questionnaire_response


def test_device_created_with_env(device: Device):
    assert device.environment == "dev"


def test_device_created_with_datetime(device: Device):
    assert isinstance(device.created_on, datetime)
    assert device.updated_on == None
    assert device.deleted_on == None


def test_device_update(device: Device):
    device_created_on = device.created_on
    device_updated_on = device.updated_on
    event = device.update(name="bar")
    assert device.name == "bar"
    assert device.deleted_on == None
    assert isinstance(device.updated_on, datetime)
    assert device.updated_on != device_updated_on
    assert device.created_on == device_created_on
    assert isinstance(event, DeviceUpdatedEvent)


def test_device_delete(device: Device):
    device_created_on = device.created_on
    assert device.deleted_on == None
    event = device.delete()
    assert device.status == Status.INACTIVE
    assert device.tags == set()
    assert device.created_on == device_created_on
    assert isinstance(device.deleted_on, datetime)
    assert device.updated_on == device.deleted_on
    assert isinstance(event, DeviceDeletedEvent)


def test_device_add_key(device: Device):
    event = device.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    assert device.keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    ]
    assert isinstance(event, DeviceKeyAddedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device.updated_on


def test_device_delete_key(device: Device):
    device.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    event = device.delete_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    assert device.keys == []
    assert isinstance(event, DeviceKeyDeletedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device.updated_on


def test_device_delete_key_fail(device: Device):
    with pytest.raises(NotFoundError):
        device.delete_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")


def test_device_add_questionnaire_response(
    device: Device,
    questionnaire_response: QuestionnaireResponse,
    another_good_questionnaire_response: QuestionnaireResponse,
):
    event = device.add_questionnaire_response(
        questionnaire_response=questionnaire_response
    )
    original_updated_on = device.updated_on

    assert device.questionnaire_responses == {
        "my-questionnaire/1": [questionnaire_response]
    }
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device.updated_on

    event_2 = device.add_questionnaire_response(
        questionnaire_response=another_good_questionnaire_response
    )

    assert device.questionnaire_responses == {
        "my-questionnaire/1": [
            questionnaire_response,
            another_good_questionnaire_response,
        ]
    }

    assert device.updated_on == event_2.updated_on
    assert device.updated_on > original_updated_on

    assert isinstance(event_2, QuestionnaireResponseUpdatedEvent)
    assert event_2.updated_on is not None
    assert event_2.updated_on > event.updated_on
    assert event_2.updated_on == device.updated_on


def test_device_cannot_add_same_questionnaire_response_twice(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    with pytest.raises(DuplicateQuestionnaireResponse):
        device.add_questionnaire_response(questionnaire_response=questionnaire_response)


def test_device_add_tag(device: Device):
    event_1 = device.add_tag(foo="first", bar="second")
    assert isinstance(event_1, DeviceTagAddedEvent)
    assert [tag.value for tag in device.tags] == ["bar=second&foo=first"]
    assert event_1.updated_on is not None
    assert event_1.updated_on == device.updated_on

    event_2 = device.add_tag(foo="first", bar="second", baz="third")
    assert event_2.updated_on is not None
    assert event_2.updated_on == device.updated_on

    with pytest.raises(DuplicateError):
        device.add_tag(bar="second", foo="first")

    assert sorted(tag.value for tag in device.tags) == sorted(
        ["bar=second&foo=first", "bar=second&baz=third&foo=first"]
    )

    assert event_2.updated_on > event_1.updated_on

    event_3 = device.clear_tags()
    assert isinstance(event_3, DeviceTagsClearedEvent)
    assert event_3.updated_on > event_2.updated_on
    assert device.tags == set()


def test_device_add_tags_in_one_go(device: Device):
    event = device.add_tags(
        tags=[
            dict(foo="first", bar="second"),
            dict(foo="first", bar="second", baz="third"),
        ]
    )
    assert isinstance(event, DeviceTagsAddedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device.updated_on

    with pytest.raises(DuplicateError):
        device.add_tags([dict(bar="second", foo="first")])

    assert sorted(tag.value for tag in device.tags) == sorted(
        ["bar=second&foo=first", "bar=second&baz=third&foo=first"]
    )


def test_device_tag_from__root__():
    tag = DeviceTag(foo="bAr", boo="FaR")
    assert tag.components == tuple((("boo", "far"), ("foo", "bar")))  # lowercased
    tag_as_dict = tag.dict()
    reconstituted_tag = DeviceTag(__root__=tag.__root__)

    assert tag_as_dict == tuple(tag.__root__)
    assert reconstituted_tag == tag
    assert reconstituted_tag in {tag}


def test_device_tag_from_kwargs():
    tag = DeviceTag(foo="bar", boo="far")
    tag_as_dict = tag.dict()
    reconstituted_tag = DeviceTag(**{k: v for k, v in tag_as_dict})

    assert tag_as_dict == tuple(tag.components)
    assert reconstituted_tag == tag
    assert reconstituted_tag in {tag}


def test_device_state_tags(device: Device):
    device.add_tag(foo="bar")
    (device_tag,) = device.tags
    (state_tag,) = device.state()["tags"]
    assert isinstance(state_tag, list)
    assert state_tag == [list(component) for component in device_tag.components]
