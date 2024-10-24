import pytest
from domain.core.questionnaire.v2 import Questionnaire
from domain.repository.questionnaire_repository.v1 import QuestionnaireRepository
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from event.json import json_load
from hypothesis import assume, given, settings
from sds.cpm_translation.tests.test_cpm_translation import (
    NHS_ACCREDITED_SYSTEM_STRATEGY,
)
from sds.cpm_translation.translations import update_in_list_of_dict
from sds.domain.nhs_accredited_system import NhsAccreditedSystem

from etl.sds.tests.constants import EtlTestDataPath


@pytest.fixture
def spine_device_questionnaire_v1() -> Questionnaire:
    repo = QuestionnaireRepository()
    return repo.read(name=QuestionnaireInstance.SPINE_DEVICE)


def _is_accredited_system(obj: dict[str, str]) -> bool:
    return obj["object_class"].lower() == NhsAccreditedSystem.OBJECT_CLASS


def _test_spine_device_questionnaire_v1(
    nhs_accredited_system: NhsAccreditedSystem, questionnaire: Questionnaire
):
    assert nhs_accredited_system.questionnaire() == questionnaire
    count_mandatory_questions = len(questionnaire.mandatory_questions)
    questionnaire_response_responses = (
        nhs_accredited_system.as_questionnaire_response_answers()
    )

    count_accredited_systems = 0
    ods_codes = nhs_accredited_system.nhs_as_client or ["ABC"]
    for ods_code in ods_codes:
        count_accredited_systems += 1
        update_in_list_of_dict(
            obj=questionnaire_response_responses, key="nhs_as_client", value=[ods_code]
        )
        _questionnaire_response = questionnaire.respond(
            responses=questionnaire_response_responses
        )
        assert (
            _questionnaire_response.questionnaire.id
            == f"{QuestionnaireInstance.SPINE_DEVICE}/1"
        )
        assert len(_questionnaire_response.answers) >= count_mandatory_questions

    assert count_accredited_systems > 0
    assert count_accredited_systems == len(ods_codes)
    return True


@settings(deadline=1500)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_spine_device_questionnaire_v1_local(
    nhs_accredited_system: NhsAccreditedSystem,
):
    assume(len(nhs_accredited_system.nhs_as_client) > 0)
    repo = QuestionnaireRepository()
    spine_device_questionnaire_v1 = repo.read(name=QuestionnaireInstance.SPINE_DEVICE)

    assert _test_spine_device_questionnaire_v1(
        nhs_accredited_system=nhs_accredited_system,
        questionnaire=spine_device_questionnaire_v1,
    )


@pytest.mark.s3(EtlTestDataPath.FULL_JSON)
def test_spine_device_questionnaire_v1_integration(
    spine_device_questionnaire_v1: Questionnaire, test_data_paths
):
    (path,) = test_data_paths
    with open(path) as f:
        data: list[dict] = json_load(f)

    for accredited_system in filter(_is_accredited_system, data):
        nhs_accredited_system = NhsAccreditedSystem.construct(**accredited_system)
        assert _test_spine_device_questionnaire_v1(
            nhs_accredited_system=nhs_accredited_system,
            questionnaire=spine_device_questionnaire_v1,
        )
