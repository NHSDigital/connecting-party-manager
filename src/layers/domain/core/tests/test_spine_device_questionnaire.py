import pytest
from domain.core.questionnaire import Question
from domain.core.spine_device_questionnaire import create_spine_device_questionnaire_v1


@pytest.mark.parametrize(
    ["name", "version"],
    [["spine_device", 1]],
)
def test_spine_device_questionnaire_v1(name: str, version: int):
    spine_device_questionnaire_v1 = create_spine_device_questionnaire_v1()

    assert spine_device_questionnaire_v1 is not None
    assert spine_device_questionnaire_v1.name == name
    assert spine_device_questionnaire_v1.version == version
    assert spine_device_questionnaire_v1.questions is not None

    Q1 = Question(
        name="ManufacturingOdsCode",
        answer_type=str,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q2 = Question(
        name="InteractionIds",
        answer_type=str,
        multiple=True,
        validation_rules=None,
        choices=None,
    )
    Q3 = Question(
        name="Owner",
        answer_type=str,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q4 = Question(
        name="PartyKey",
        answer_type=str,
        multiple=False,
        validation_rules=None,
        choices=None,
    )

    assert Q1.name in spine_device_questionnaire_v1.questions
    assert Q2.name in spine_device_questionnaire_v1.questions
    assert Q3.name in spine_device_questionnaire_v1.questions
    assert Q4.name in spine_device_questionnaire_v1.questions

    assert Q1 == spine_device_questionnaire_v1.questions[Q1.name]
    assert Q2 == spine_device_questionnaire_v1.questions[Q2.name]
    assert Q3 == spine_device_questionnaire_v1.questions[Q3.name]
    assert Q4 == spine_device_questionnaire_v1.questions[Q4.name]
