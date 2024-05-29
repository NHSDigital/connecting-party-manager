from datetime import datetime
from itertools import chain

import pytest
from domain.core.device import (
    Device,
    DeviceIndexAddedEvent,
    DeviceKeyAddedEvent,
    DeviceKeyDeletedEvent,
    DeviceStatus,
    DeviceType,
    DeviceUpdatedEvent,
    QuestionnaireNotFoundError,
    QuestionnaireResponseNotFoundError,
    QuestionNotFoundError,
    _get_questionnaire_responses,
    _get_unique_answers,
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
    assert device.status == DeviceStatus.INACTIVE
    assert device.created_on == device_created_on
    assert isinstance(device.deleted_on, datetime)
    assert device.updated_on == device.deleted_on
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


def test__get_unique_answers():
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="question1", multiple=True)
    questionnaire_response_1 = questionnaire.respond(
        [
            {"question1": ["foo"]},
            {"question1": ["bar"]},
            {"question1": ["foo"]},
        ]
    )

    questionnaire_response_2 = questionnaire.respond(
        [
            {"question1": ["baz", "BAR"]},
            {"question1": ["foo"]},
        ]
    )

    questionnaire_response_3 = questionnaire.respond(
        [
            {"question1": ["FOO"]},
            {"question1": ["bar"]},
            {"question1": ["foo"]},
        ]
    )

    unique_answers = _get_unique_answers(
        questionnaire_responses=[
            questionnaire_response_1,
            questionnaire_response_2,
            questionnaire_response_3,
        ],
        question_name="question1",
    )

    assert unique_answers == {"foo", "bar", "FOO", "BAR", "baz"}


def test__get_questionnaire_responses():
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="question1")
    questionnaire_response = questionnaire.respond([{"question1": ["foo"]}])
    questionnaire_responses = [questionnaire_response]
    assert (
        _get_questionnaire_responses(
            questionnaire_responses={questionnaire.id: questionnaire_responses},
            questionnaire_id=questionnaire.id,
        )
        == questionnaire_responses
    )


def test_device_add_index(device: Device):
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="question1", multiple=True)

    N_QUESTIONNAIRE_RESPONSES = 123
    N_UNIQUE_ANSWERS = 7

    answers = [["a", "b", "c"], ["d"], ["e", "f", "g"], ["a"], ["b", "c"]]
    assert len(set(chain.from_iterable(answers))) == N_UNIQUE_ANSWERS

    for _ in range(N_QUESTIONNAIRE_RESPONSES):
        for _answers in answers:
            questionnaire_response = questionnaire.respond(
                responses=[{"question1": _answers}]
            )
            device.add_questionnaire_response(
                questionnaire_response=questionnaire_response
            )

    events = device.add_index(questionnaire_id="foo/1", question_name="question1")
    assert len(events) == N_UNIQUE_ANSWERS
    assert all(isinstance(event, DeviceIndexAddedEvent) for event in events)


def test_device_add_index_no_such_questionnaire(device: Device):
    with pytest.raises(QuestionnaireNotFoundError):
        device.add_index(questionnaire_id="foo/1", question_name="question1")


def test_device_add_index_no_such_questionnaire_response(device: Device):
    device.questionnaire_responses["foo/1"] = []
    with pytest.raises(QuestionnaireResponseNotFoundError):
        device.add_index(questionnaire_id="foo/1", question_name="question1")


def test_device_add_index_no_such_question(device: Device):
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire_response = questionnaire.respond(responses=[])
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)

    with pytest.raises(QuestionNotFoundError):
        device.add_index(questionnaire_id="foo/1", question_name="question1")
