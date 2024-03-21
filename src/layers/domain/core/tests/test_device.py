import pytest
from domain.core.device import (
    Device,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceStatus,
    DeviceType,
    DeviceUpdatedEvent,
    QuestionnaireNotFoundError,
    QuestionnaireResponseNotFoundError,
)
from domain.core.device_key import DeviceKey, DeviceKeyType
from domain.core.error import NotFoundError
from domain.core.questionnaire import (
    Questionnaire,
    QuestionnaireInstanceEvent,
    QuestionnaireResponse,
    QuestionnaireResponseAddedEvent,
    QuestionnaireResponseDeletedEvent,
    QuestionnaireResponseUpdatedEvent,
)


@pytest.fixture
def device():
    return Device(
        name="Foo",
        ods_code="ABC123",
        product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
        type=DeviceType.PRODUCT,
    )


@pytest.fixture
def questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["hi"]}])


@pytest.fixture
def another_good_questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["bye"]}])


@pytest.fixture
def another_questionnaire_response() -> QuestionnaireResponse:
    questionnaire = Questionnaire(name="bar", version=1)
    questionnaire.add_question(name="question1")
    return questionnaire.respond(responses=[{"question1": ["bye"]}])


def test_device_update(device: Device):
    event = device.update(name="bar")
    assert device.name == "bar"
    assert isinstance(event, DeviceUpdatedEvent)


def test_device_delete(device: Device):
    event = device.delete()
    assert device.status == DeviceStatus.INACTIVE
    assert isinstance(event, DeviceUpdatedEvent)


def test_device_add_key(device: Device):
    event = device.add_key(type=DeviceKeyType.PRODUCT_ID, key="P.XXX-YYY")
    assert device.keys == {
        "P.XXX-YYY": DeviceKey(type=DeviceKeyType.PRODUCT_ID, key="P.XXX-YYY")
    }
    assert isinstance(event, DeviceKeyAddedEvent)


def test_device_delete_key(device: Device):
    device.add_key(type=DeviceKeyType.PRODUCT_ID, key="P.XXX-YYY")
    event = device.delete_key(key="P.XXX-YYY")
    assert device.keys == {}
    assert isinstance(event, DeviceKeyDeletedEvent)


def test_device_delete_key_fail(device: Device):
    with pytest.raises(NotFoundError):
        device.delete_key(key="P.XXX-YYY")


def test_device_add_questionnaire_response(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    events = device.add_questionnaire_response(
        questionnaire_response=questionnaire_response
    )
    assert device.questionnaire_responses == {"foo/1": [questionnaire_response]}
    assert len(events) == 2
    assert isinstance(events[0], QuestionnaireInstanceEvent)
    assert isinstance(events[1], QuestionnaireResponseAddedEvent)

    events = device.add_questionnaire_response(
        questionnaire_response=questionnaire_response
    )
    assert device.questionnaire_responses == {
        "foo/1": [questionnaire_response, questionnaire_response]
    }
    assert len(events) == 1
    assert isinstance(events[0], QuestionnaireResponseAddedEvent)


def test_device_update_questionnaire_response(
    device: Device,
    questionnaire_response: QuestionnaireResponse,
    another_good_questionnaire_response: QuestionnaireResponse,
):
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    event = device.update_questionnaire_response(
        questionnaire_response=another_good_questionnaire_response,
        questionnaire_response_index=0,
    )

    assert device.questionnaire_responses == {
        "foo/1": [another_good_questionnaire_response]
    }
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)


def test_device_update_questionnaire_response_index_error(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    with pytest.raises(QuestionnaireResponseNotFoundError):
        device.update_questionnaire_response(
            questionnaire_response=questionnaire_response,
            questionnaire_response_index=1,
        )


def test_device_update_questionnaire_response_key_error(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    with pytest.raises(QuestionnaireNotFoundError):
        device.update_questionnaire_response(
            questionnaire_response=questionnaire_response,
            questionnaire_response_index=0,
        )


def test_device_delete_questionnaire_response(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    event = device.delete_questionnaire_response(
        questionnaire_id="foo/1", questionnaire_response_index=0
    )
    assert device.questionnaire_responses == {}
    assert isinstance(event, QuestionnaireResponseDeletedEvent)


def test_device_delete_questionnaire_response_index_error(
    device: Device, questionnaire_response: QuestionnaireResponse
):
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    with pytest.raises(QuestionnaireResponseNotFoundError):
        device.delete_questionnaire_response(
            questionnaire_id="foo/1", questionnaire_response_index=1
        )


def test_device_delete_questionnaire_response_key_error(device: Device):
    with pytest.raises(QuestionnaireNotFoundError):
        device.delete_questionnaire_response(
            questionnaire_id="bar/1", questionnaire_response_index=0
        )
