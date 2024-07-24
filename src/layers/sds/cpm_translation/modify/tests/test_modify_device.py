import pytest
from domain.core.device import Device, DeviceType
from domain.core.questionnaire import (
    Questionnaire,
    QuestionnaireResponse,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.root import Root
from pydantic import ValidationError
from sds.cpm_translation.modify.modify_device import (
    CannotDeleteMandatoryField,
    NothingToDelete,
    _as_questionnaire_response_answer,
    new_questionnaire_response_from_template,
    update_device_metadata,
)
from sds.domain.constants import ModificationType


def _sort_key(obj):
    if isinstance(obj, list):
        return tuple(obj)
    if isinstance(obj, dict):
        return tuple(map(tuple, obj.items()))
    return obj


def _sort(obj):
    if isinstance(obj, list):
        return sorted((_sort(item) for item in obj), key=_sort_key)
    if isinstance(obj, dict):
        return {k: _sort(v) for k, v in obj.items()}
    return obj


class MyModel:
    @classmethod
    def get_field_name_for_alias(cls, alias):
        return alias

    @classmethod
    def parse_and_validate_field(cls, field, value):
        return value

    @classmethod
    def is_mandatory_field(cls, field):
        return False


@pytest.mark.parametrize("x", ["foo", 123, True, None, {"foo": "bar"}, ("foo",)])
def test__as_questionnaire_response_answer_not_list_or_set(x):
    assert _as_questionnaire_response_answer(x) == [x]


@pytest.mark.parametrize("x", [["foo", "bar"], {"foo", "bar"}])
def test__as_questionnaire_response_answer_list_or_set(x):
    assert _as_questionnaire_response_answer(x) == list(x)


@pytest.fixture
def questionnaire_response():
    _questionnaire = Questionnaire(name="my_questionnaire", version=1)
    _questionnaire.add_question(name="hello", answer_types=(str,))
    _questionnaire.add_question(name="foo", answer_types=(str,), multiple=True)
    _questionnaire_response = _questionnaire.respond(
        responses=[{"hello": ["world"]}, {"foo": ["bar", "baz"]}]
    )
    return _questionnaire_response


@pytest.fixture
def device(questionnaire_response):
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    _device = product_team.create_device(name="foo", device_type=DeviceType.PRODUCT)
    _device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    return _device


def test_new_questionnaire_response_from_template_modification(
    questionnaire_response,
):
    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update="hello",
        value="whatever",
    )
    assert new_questionnaire_response.responses == [
        {"hello": ["whatever"]},
        {"foo": ["bar", "baz"]},
    ]


def test_new_questionnaire_response_from_template_deletion(
    questionnaire_response,
):
    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update="hello",
        value=[],
    )
    assert new_questionnaire_response.responses == [
        {"foo": ["bar", "baz"]},
    ]


@pytest.mark.parametrize(
    ["modification_type", "field_alias", "new_values"],
    (
        [
            ModificationType.ADD,
            "hello",
            ["WORLD"],
        ],
        [
            ModificationType.REPLACE,
            "hello",
            ["world", "WORLD"],
        ],
    ),
)
def test_update_device_metadata_add_or_replace_non_empty_data_to_non_multiple(
    modification_type,
    field_alias,
    new_values,
    device,
):
    with pytest.raises(ValidationError) as error:
        update_device_metadata(
            device=device,
            model=MyModel,
            modification_type=modification_type,
            field_alias=field_alias,
            new_values=new_values,
        )
    assert "Question 'hello' does not allow multiple responses" in str(error.value)


@pytest.mark.parametrize(
    ["modification_type", "field_alias", "new_values", "expected_responses"],
    [
        (
            ModificationType.ADD,
            "foo",
            ["BAR"],
            [{"hello": ["world"]}, {"foo": ["bar", "baz", "BAR"]}],
        ),
        (
            ModificationType.ADD,
            "hello",
            [],
            [{"hello": ["world"]}, {"foo": ["bar", "baz"]}],
        ),
        (
            ModificationType.ADD,
            "foo",
            ["BAR", "baz", "BAR"],
            [
                {"hello": ["world"]},
                {"foo": ["bar", "baz", "BAR"]},
            ],
        ),
        (
            ModificationType.REPLACE,
            "foo",
            ["BAR", "baz", "BAR"],
            [
                {"hello": ["world"]},
                {"foo": ["baz", "BAR"]},
            ],
        ),
        (
            ModificationType.DELETE,
            "foo",
            ["anything"],
            [{"hello": ["world"]}],
        ),
    ],
)
def test_update_device_metadata(
    modification_type,
    field_alias,
    new_values,
    expected_responses,
    device: Device,
    questionnaire_response: QuestionnaireResponse,
):
    events_before = list(device.events)

    _device = update_device_metadata(
        device=device,
        model=MyModel,
        modification_type=modification_type,
        field_alias=field_alias,
        new_values=new_values,
    )

    assert _device is device
    assert len(_device.events) == len(events_before) + 1
    assert all(event in _device.events for event in events_before)
    assert isinstance(_device.events[-1], QuestionnaireResponseUpdatedEvent)

    device_metadata = _device.questionnaire_responses[
        questionnaire_response.questionnaire.id
    ][0].responses
    assert _sort(device_metadata) == _sort(expected_responses)


def test_update_device_metadata_delete_mandatory_field(device):
    class _MyModel(MyModel):
        @classmethod
        def is_mandatory_field(cls, field):
            return True

    with pytest.raises(CannotDeleteMandatoryField):
        update_device_metadata(
            device=device,
            model=_MyModel,
            modification_type=ModificationType.DELETE,
            field_alias="foo",
            new_values=[],
        )

    with pytest.raises(CannotDeleteMandatoryField):
        update_device_metadata(
            device=device,
            model=_MyModel,
            modification_type=ModificationType.REPLACE_WITH_EMPTY,
            field_alias="foo",
            new_values=[],
        )


def test_update_device_metadata_delete_field_that_doesnt_exist(device):
    with pytest.raises(NothingToDelete):
        update_device_metadata(
            device=device,
            model=MyModel,
            modification_type=ModificationType.DELETE,
            field_alias="bar",
            new_values=[],
        )
