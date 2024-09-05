from datetime import datetime

import pytest
from domain.core.device.v2 import (
    Device,
    DeviceDeletedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceTag,
    DeviceTagAddedEvent,
    DeviceTagsAddedEvent,
    DeviceTagsClearedEvent,
    DeviceType,
    DeviceUpdatedEvent,
    DuplicateQuestionnaireResponse,
    QuestionnaireNotFoundError,
    QuestionnaireResponseNotFoundError,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key.v2 import DeviceKey, DeviceKeyType
from domain.core.enum import Status
from domain.core.error import DuplicateError, NotFoundError
from domain.core.questionnaire.v2 import Questionnaire, QuestionnaireResponse


@pytest.fixture
def device_v2():
    return Device(
        name="Foo",
        ods_code="ABC123",
        product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
        device_type=DeviceType.PRODUCT,
    )


@pytest.fixture
def questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="foo", version=2)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["hi"]}])


@pytest.fixture
def another_good_questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="foo", version=2)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["bye"]}])


@pytest.fixture
def another_questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="bar", version=2)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["bye"]}])


def test_device_created_with_datetime(device_v2: Device):
    assert isinstance(device_v2.created_on, datetime)
    assert device_v2.updated_on == None
    assert device_v2.deleted_on == None


def test_device_update(device_v2: Device):
    device_created_on = device_v2.created_on
    device_updated_on = device_v2.updated_on
    event = device_v2.update(name="bar")
    assert device_v2.name == "bar"
    assert device_v2.deleted_on == None
    assert isinstance(device_v2.updated_on, datetime)
    assert device_v2.updated_on != device_updated_on
    assert device_v2.created_on == device_created_on
    assert isinstance(event, DeviceUpdatedEvent)


def test_device_delete(device_v2: Device):
    device_created_on = device_v2.created_on
    assert device_v2.deleted_on == None
    event = device_v2.delete()
    assert device_v2.status == Status.INACTIVE
    assert device_v2.tags == set()
    assert device_v2.created_on == device_created_on
    assert isinstance(device_v2.deleted_on, datetime)
    assert device_v2.updated_on == device_v2.deleted_on
    assert isinstance(event, DeviceDeletedEvent)


def test_device_add_key(device_v2: Device):
    event = device_v2.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    assert device_v2.keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    ]
    assert isinstance(event, DeviceKeyAddedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device_v2.updated_on


def test_device_delete_key(device_v2: Device):
    device_v2.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    event = device_v2.delete_key(
        key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY"
    )
    assert device_v2.keys == []
    assert isinstance(event, DeviceKeyDeletedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device_v2.updated_on


def test_device_delete_key_fail(device_v2: Device):
    with pytest.raises(NotFoundError):
        device_v2.delete_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")


def test_device_add_questionnaire_response(
    device_v2: Device,
    questionnaire_response: QuestionnaireResponse,
    another_good_questionnaire_response: QuestionnaireResponse,
):
    event = device_v2.add_questionnaire_response(
        questionnaire_response=questionnaire_response
    )
    created_on_1 = questionnaire_response.created_on.isoformat()
    original_updated_on = device_v2.updated_on
    assert device_v2.questionnaire_responses == {
        "foo/2": {created_on_1: questionnaire_response}
    }
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device_v2.updated_on

    event_2 = device_v2.add_questionnaire_response(
        questionnaire_response=another_good_questionnaire_response
    )
    created_on_2 = another_good_questionnaire_response.created_on.isoformat()
    assert device_v2.questionnaire_responses == {
        "foo/2": {
            created_on_1: questionnaire_response,
            created_on_2: another_good_questionnaire_response,
        }
    }

    assert device_v2.updated_on == event_2.updated_on
    assert device_v2.updated_on > original_updated_on

    assert isinstance(event_2, QuestionnaireResponseUpdatedEvent)
    assert event_2.updated_on is not None
    assert event_2.updated_on > event.updated_on
    assert event_2.updated_on == device_v2.updated_on


def test_device_cannot_add_same_questionnaire_response_twice(
    device_v2: Device, questionnaire_response: QuestionnaireResponse
):
    device_v2.add_questionnaire_response(questionnaire_response=questionnaire_response)
    with pytest.raises(DuplicateQuestionnaireResponse):
        device_v2.add_questionnaire_response(
            questionnaire_response=questionnaire_response
        )


def test_device_update_questionnaire_response(
    device_v2: Device,
    questionnaire_response: QuestionnaireResponse,
    another_good_questionnaire_response: QuestionnaireResponse,
):
    created_on = questionnaire_response.created_on
    another_good_questionnaire_response.created_on = created_on

    device_v2.add_questionnaire_response(questionnaire_response=questionnaire_response)
    event = device_v2.update_questionnaire_response(
        questionnaire_response=another_good_questionnaire_response
    )
    assert device_v2.questionnaire_responses == {
        "foo/2": {created_on.isoformat(): another_good_questionnaire_response}
    }
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device_v2.updated_on


def test_device_update_questionnaire_response_mismatching_created_on_error(
    device_v2: Device,
    questionnaire_response: QuestionnaireResponse,
    another_good_questionnaire_response: QuestionnaireResponse,
):
    device_v2.add_questionnaire_response(questionnaire_response=questionnaire_response)
    with pytest.raises(QuestionnaireResponseNotFoundError):
        device_v2.update_questionnaire_response(
            questionnaire_response=another_good_questionnaire_response
        )


def test_device_update_questionnaire_response_key_error(
    device_v2: Device, questionnaire_response: QuestionnaireResponse
):
    with pytest.raises(QuestionnaireNotFoundError):
        device_v2.update_questionnaire_response(
            questionnaire_response=questionnaire_response
        )


def test_device_add_tag(device_v2: Device):
    event_1 = device_v2.add_tag(foo="first", bar="second")
    assert isinstance(event_1, DeviceTagAddedEvent)
    assert [tag.value for tag in device_v2.tags] == [
        "<<bar##second>>##<<foo##first>>",
    ]
    assert event_1.updated_on is not None
    assert event_1.updated_on == device_v2.updated_on

    event_2 = device_v2.add_tag(foo="first", bar="second", baz="third")
    assert event_2.updated_on is not None
    assert event_2.updated_on == device_v2.updated_on

    with pytest.raises(DuplicateError):
        device_v2.add_tag(bar="second", foo="first")

    assert sorted(tag.value for tag in device_v2.tags) == sorted(
        [
            "<<bar##second>>##<<foo##first>>",
            "<<bar##second>>##<<baz##third>>##<<foo##first>>",
        ]
    )

    assert event_2.updated_on > event_1.updated_on

    event_3 = device_v2.clear_tags()
    assert isinstance(event_3, DeviceTagsClearedEvent)
    assert event_3.updated_on > event_2.updated_on
    assert device_v2.tags == set()


def test_device_add_tags_in_one_go(device_v2: Device):
    event = device_v2.add_tags(
        tags=[
            dict(foo="first", bar="second"),
            dict(foo="first", bar="second", baz="third"),
        ]
    )
    assert isinstance(event, DeviceTagsAddedEvent)
    assert event.updated_on is not None
    assert event.updated_on == device_v2.updated_on

    with pytest.raises(DuplicateError):
        device_v2.add_tags([dict(bar="second", foo="first")])

    assert sorted(tag.value for tag in device_v2.tags) == sorted(
        [
            "<<bar##second>>##<<foo##first>>",
            "<<bar##second>>##<<baz##third>>##<<foo##first>>",
        ]
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


def test_device_state_tags(device_v2: Device):
    device_v2.add_tag(foo="bar")
    (device_tag,) = device_v2.tags
    (state_tag,) = device_v2.state()["tags"]
    assert isinstance(state_tag, list)
    assert state_tag == [list(component) for component in device_tag.components]
