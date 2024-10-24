import pytest
from domain.core.questionnaire.v2 import Questionnaire
from domain.repository.questionnaire_repository import QuestionnaireRepository
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from event.json import json_load
from hypothesis import given, settings
from sds.cpm_translation.tests.test_cpm_translation import NHS_MHS_STRATEGY
from sds.domain.nhs_mhs import NhsMhs

from etl.sds.tests.constants import EtlTestDataPath


@pytest.fixture
def spine_endpoint_questionnaire_v1() -> Questionnaire:
    repo = QuestionnaireRepository()
    return repo.read(name=QuestionnaireInstance.SPINE_ENDPOINT)


def _mhs(obj: dict[str, str]) -> bool:
    return obj["object_class"].lower() == NhsMhs.OBJECT_CLASS


def _test_spine_endpoint_questionnaire_v1(
    nhs_mhs: NhsMhs, questionnaire: Questionnaire
):
    assert nhs_mhs.questionnaire() == questionnaire
    count_mandatory_questions = len(questionnaire.mandatory_questions)
    questionnaire_response_answers = nhs_mhs.as_questionnaire_response_answers()

    _questionnaire_response = questionnaire.respond(
        responses=questionnaire_response_answers
    )
    assert (
        _questionnaire_response.questionnaire.id
        == f"{QuestionnaireInstance.SPINE_ENDPOINT}/1"
    )
    assert len(_questionnaire_response.answers) >= count_mandatory_questions
    return True


@settings(deadline=1500)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_spine_endpoint_questionnaire_v1_local(nhs_mhs: NhsMhs):
    repo = QuestionnaireRepository()
    spine_endpoint_questionnaire_v1 = repo.read(
        name=QuestionnaireInstance.SPINE_ENDPOINT
    )

    assert _test_spine_endpoint_questionnaire_v1(
        nhs_mhs=nhs_mhs, questionnaire=spine_endpoint_questionnaire_v1
    )


@pytest.mark.s3(EtlTestDataPath.FULL_JSON)
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
