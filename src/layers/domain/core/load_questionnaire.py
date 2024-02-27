from pathlib import Path

from domain.core.questionnaire_validation_custom_rules import empty_str, url
from event.json import json_load

from .questionnaire import ALLOWED_QUESTION_TYPES, Questionnaire

PATH_TO_HERE = Path(__file__).parent

VALIDATION_RULE_MAPPING = {
    "empty_str": empty_str,
    "url": url,
}


def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json_load(file)
    return data


def process_answer_types(answer_types):
    answer_types = set(
        _type for _type in ALLOWED_QUESTION_TYPES if _type.__name__ in answer_types
    )

    return answer_types


def process_validation_rules(validation_rules):
    return [VALIDATION_RULE_MAPPING[rule] for rule in validation_rules]


def render_questionnaire(questionnaire_name, questionnaire_version):
    json_file_path = f"{PATH_TO_HERE}/questionnaires/{questionnaire_name}/v{questionnaire_version}.json"
    questions = load_json_file(json_file_path)
    questionnaire = Questionnaire(
        name=questionnaire_name, version=questionnaire_version
    )

    for question in questions:
        # Convert answer_type string to Python type
        if "answer_types" in question:
            question["answer_types"] = process_answer_types(question["answer_types"])

        if "validation_rules" in question:
            question["validation_rules"] = process_validation_rules(
                question["validation_rules"]
            )

        questionnaire.add_question(**question)

    return questionnaire
