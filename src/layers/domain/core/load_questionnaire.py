from pathlib import Path

from domain.core import questionnaire_validation_custom_rules
from event.json import json_load

from .questionnaire import ALLOWED_QUESTION_TYPES, Questionnaire

PATH_TO_HERE = Path(__file__).parent


def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json_load(file)
    return data


def convert_answer_type_names_to_python_types(answer_types):
    answer_types = set(
        _type for _type in ALLOWED_QUESTION_TYPES if _type.__name__ in answer_types
    )

    return answer_types


def convert_rule_names_to_rule_functions(validation_rules):
    return [
        getattr(questionnaire_validation_custom_rules, rule)
        for rule in validation_rules
    ]


def render_question(question):
    if "answer_types" in question:
        question["answer_types"] = convert_answer_type_names_to_python_types(
            question["answer_types"]
        )

    if "validation_rules" in question:
        question["validation_rules"] = convert_rule_names_to_rule_functions(
            question["validation_rules"]
        )

    return question


def render_questionnaire(
    questionnaire_name: str, questionnaire_version: int
) -> Questionnaire:
    json_file_path = f"{PATH_TO_HERE}/questionnaires/{questionnaire_name}/v{questionnaire_version}.json"
    questions = load_json_file(json_file_path)
    questionnaire = Questionnaire(
        name=questionnaire_name, version=questionnaire_version
    )
    for question in map(render_question, questions):
        questionnaire.add_question(**question)

    return questionnaire
