import pytest
from domain.core.load_questionnaire import render_questionnaire
from domain.core.questionnaire import Questionnaire
from domain.core.questionnaires import QuestionnaireInstance
from event.json import json_load
from hypothesis import given
from sds.cpm_translation.tests.test_cpm_translation import NHS_MHS_STRATEGY
from sds.domain.nhs_mhs import NhsMhs


@pytest.fixture
def spine_endpoint_questionnaire_v1() -> Questionnaire:
    return render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT,
        questionnaire_version=1,
    )


def _mhs(obj: dict[str, str]) -> bool:
    return obj["object_class"].lower() == NhsMhs.OBJECT_CLASS


def _test_spine_endpoint_questionnaire_v1(
    nhs_mhs: NhsMhs, questionnaire: Questionnaire
):
    count_mandatory_questions = len(questionnaire.mandatory_questions)
    questionnaire_response_responses = nhs_mhs.as_questionnaire_response_responses()

    _questionnaire_response = questionnaire.respond(
        responses=questionnaire_response_responses
    )
    assert (
        _questionnaire_response.questionnaire.id
        == f"{QuestionnaireInstance.SPINE_ENDPOINT}/1"
    )
    assert len(_questionnaire_response.responses) >= count_mandatory_questions
    return True


@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_spine_endpoint_questionnaire_v1_local(nhs_mhs: NhsMhs):
    spine_endpoint_questionnaire_v1 = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT,
        questionnaire_version=1,
    )
    assert _test_spine_endpoint_questionnaire_v1(
        nhs_mhs=nhs_mhs, questionnaire=spine_endpoint_questionnaire_v1
    )


@pytest.mark.s3("sds/etl/bulk/1701246-fix-18032023.json")
def test_spine_endpoint_questionnaire_v1_integration(
    spine_endpoint_questionnaire_v1: Questionnaire, test_data_paths
):
    (path,) = test_data_paths
    with open(path) as f:
        data: list[dict] = json_load(f)

    for mhs in filter(_mhs, data):
        nhs_mhs = NhsMhs.construct(**mhs)
        assert _test_spine_endpoint_questionnaire_v1(
            nhs_mhs=nhs_mhs, questionnaire=spine_endpoint_questionnaire_v1
        )
