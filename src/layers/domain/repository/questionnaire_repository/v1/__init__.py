from pathlib import Path

from domain.core.questionnaire.v2 import Questionnaire
from domain.repository.errors import ItemNotFound
from event.json import json_load

from .deserialisers import QUESTION_DESERIALISERS

PATH_TO_QUESTIONNAIRES = Path(__file__).parent / "questionnaires"


def deserialise_question(question: dict) -> dict:
    for field, deserialiser in QUESTION_DESERIALISERS.items():
        value = question.get(field)
        if value:
            question[field] = deserialiser(value)
    return question


def version_from_file_path(file_path: Path) -> int:
    return int(file_path.stem.lstrip("v"))


def get_latest_questions_by_name(name: str) -> Path | None:
    possible_paths = PATH_TO_QUESTIONNAIRES.glob(f"{name}/v*.json")
    paths_sorted_by_version = sorted(possible_paths, key=version_from_file_path)
    try:
        path = paths_sorted_by_version[-1]
    except IndexError:
        path = None
    return path


def read_questions(path: Path):
    with open(path, "r") as fp:
        raw_questions = json_load(fp)
    return list(map(deserialise_question, raw_questions))


class QuestionnaireRepository:

    def read(self, name: str) -> Questionnaire:
        path = get_latest_questions_by_name(name=name)
        if not path:
            raise ItemNotFound(name, item_type=Questionnaire)

        version = version_from_file_path(path)
        questions = read_questions(path=path)
        questionnaire = Questionnaire(name=name, version=version)
        for question in questions:
            questionnaire.add_question(**question)
        return questionnaire
