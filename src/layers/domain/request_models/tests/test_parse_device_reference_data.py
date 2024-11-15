import pytest
from domain.request_models import CreateDeviceReferenceMessageSetsDataParams
from pydantic import ValidationError


def test_device_reference_data_message_set_questionnaire_default():
    params = CreateDeviceReferenceMessageSetsDataParams()
    params.questionnaire_responses["spine_mhs_message_sets"].append("foo")
    assert params.questionnaire_responses == {"spine_mhs_message_sets": ["foo"]}


def test_device_reference_data_message_set_questionnaire_bad_questionnaire_name():
    with pytest.raises(ValidationError):
        CreateDeviceReferenceMessageSetsDataParams(questionnaire_responses={"foo": []})


def test_device_reference_data_message_set_questionnaire_good_questionnaire_name():
    data = {"spine_mhs_message_sets": [{"foo": "bar"}]}
    params = CreateDeviceReferenceMessageSetsDataParams(questionnaire_responses=data)
    assert params.questionnaire_responses == data
