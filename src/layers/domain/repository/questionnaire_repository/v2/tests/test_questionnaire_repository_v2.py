from collections import defaultdict

import pytest
from domain.repository.errors import ItemNotFound
from domain.repository.questionnaire_repository.v2 import (
    PATH_TO_QUESTIONNAIRES,
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v2.questionnaires import (
    QuestionnaireInstance,
)


def test_no_zombie_questionnaires():
    possible_paths = PATH_TO_QUESTIONNAIRES.glob("*/v*.json")

    questionnaires = defaultdict(list)
    for path in possible_paths:
        questionnaires[path.parent.name].append(path.stem)

    questionnaire_names_in_repo = sorted(questionnaires.keys())
    questionnaire_names_in_enum = sorted(QuestionnaireInstance._member_map_.values())
    assert questionnaire_names_in_repo == questionnaire_names_in_enum


@pytest.mark.parametrize(
    "questionnaire_name", QuestionnaireInstance._member_map_.values()
)
def test_questionnaire_repository_read(questionnaire_name):
    questionnaire = QuestionnaireRepository().read(questionnaire_name)
    assert questionnaire.name == questionnaire_name
    assert questionnaire.version == "1"
    assert isinstance(questionnaire.json_schema, dict)


def test_questionnaire_repository_read_not_found():
    repo = QuestionnaireRepository()
    with pytest.raises(ItemNotFound):
        repo.read(name="oops")
