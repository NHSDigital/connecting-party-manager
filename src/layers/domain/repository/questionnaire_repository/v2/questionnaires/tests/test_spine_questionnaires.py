from domain.repository.questionnaire_repository.v2 import (
    PATH_TO_QUESTIONNAIRES,
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v2.questionnaires import (
    QuestionnaireInstance,
)
from event.json import json_load
from hypothesis import given, settings
from sds.cpm_translation.tests.test_cpm_translation import (
    NHS_ACCREDITED_SYSTEM_STRATEGY,
    NHS_MHS_STRATEGY,
)
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs


def _apply_field_mapping(name: str, data: dict) -> dict:
    with open(PATH_TO_QUESTIONNAIRES / name / "field_mapping.json") as f:
        field_mapping = json_load(f)
    return {field_mapping[k]: v for k, v in data.items() if k in field_mapping}


@settings(deadline=1500)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_spine_as_questionnaires_pass(nhs_accredited_system: NhsAccreditedSystem):
    as_questionnaire = QuestionnaireRepository().read(QuestionnaireInstance.SPINE_AS)
    as_interactions_questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    _as_data = nhs_accredited_system.export()
    as_data = _apply_field_mapping(name=QuestionnaireInstance.SPINE_AS, data=_as_data)
    as_interactions_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS, data=_as_data
    )

    # minus one because object_class is dropped by _apply_field_mapping
    assert len(as_data) + len(as_interactions_data) == len(_as_data) - 1

    response = as_questionnaire.validate(as_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_AS
    assert response.questionnaire_version == "1"
    assert response.data == as_data

    # Answer the additional_interactions questionnaire once per Interaction Id
    for interaction_id in as_interactions_data["Interaction Id"]:
        _as_interaction_data = {"Interaction Id": interaction_id}
        response = as_interactions_questionnaire.validate(_as_interaction_data)
        assert (
            response.questionnaire_name
            == QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        assert response.questionnaire_version == "1"
        assert response.data == _as_interaction_data


@settings(deadline=1500)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_spine_mhs_questionnaires_pass(nhs_mhs: NhsMhs):
    mhs_questionnaire = QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS)
    mhs_interactions_questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    _mhs_data = nhs_mhs.export()
    mhs_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS, data=_mhs_data
    )
    mhs_interactions_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS, data=_mhs_data
    )
    # minus one because object_class is dropped by _apply_field_mapping
    assert len(mhs_data) + len(mhs_interactions_data) == len(_mhs_data) - 1

    response = mhs_questionnaire.validate(mhs_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_MHS
    assert response.questionnaire_version == "1"
    assert response.data == mhs_data

    response = mhs_interactions_questionnaire.validate(mhs_interactions_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    assert response.questionnaire_version == "1"
    assert response.data == mhs_interactions_data