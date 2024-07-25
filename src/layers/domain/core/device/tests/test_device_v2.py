from datetime import datetime

import pytest
from domain.core.device.v2 import (
    Device,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceStatus,
    DeviceTagAddedEvent,
    DeviceType,
    DeviceUpdatedEvent,
    DuplicateQuestionnaireResponse,
    Questionnaire,
    QuestionnaireNotFoundError,
    QuestionnaireResponse,
    QuestionnaireResponseAddedEvent,
    QuestionnaireResponseNotFoundError,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key.v2 import DeviceKey, DeviceKeyType
from domain.core.error import NotFoundError


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
    assert device_v2.status == DeviceStatus.INACTIVE
    assert device_v2.created_on == device_created_on
    assert isinstance(device_v2.deleted_on, datetime)
    assert device_v2.updated_on == device_v2.deleted_on
    assert isinstance(event, DeviceUpdatedEvent)


def test_device_add_key(device_v2: Device):
    event = device_v2.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    assert device_v2.keys == [
        DeviceKey(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    ]
    assert isinstance(event, DeviceKeyAddedEvent)


def test_device_delete_key(device_v2: Device):
    device_v2.add_key(key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY")
    event = device_v2.delete_key(
        key_type=DeviceKeyType.PRODUCT_ID, key_value="P.XXX-YYY"
    )
    assert device_v2.keys == []
    assert isinstance(event, DeviceKeyDeletedEvent)


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
    created_on_1 = questionnaire_response.created_on

    assert device_v2.questionnaire_responses == {
        "foo/2": {created_on_1: questionnaire_response}
    }
    assert isinstance(event, QuestionnaireResponseAddedEvent)

    event_2 = device_v2.add_questionnaire_response(
        questionnaire_response=another_good_questionnaire_response
    )
    created_on_2 = another_good_questionnaire_response.created_on
    assert device_v2.questionnaire_responses == {
        "foo/2": {
            created_on_1: questionnaire_response,
            created_on_2: another_good_questionnaire_response,
        }
    }
    assert isinstance(event_2, QuestionnaireResponseAddedEvent)


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
        "foo/2": {created_on: another_good_questionnaire_response}
    }
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)


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
    event = device_v2.add_tag(foo="first", bar="second")
    assert isinstance(event, DeviceTagAddedEvent)
    assert [tag.value for tag in device_v2.tags] == [
        "<<foo##first>>##<<bar##second>>",
    ]

    device_v2.add_tag(foo="first", bar="second", baz="third")
    device_v2.add_tag(bar="second", foo="first")

    assert [tag.value for tag in device_v2.tags] == [
        "<<foo##first>>##<<bar##second>>",
        "<<foo##first>>##<<bar##second>>##<<baz##third>>",
        "<<bar##second>>##<<foo##first>>",
    ]
