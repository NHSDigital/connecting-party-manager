from pathlib import Path

from domain.core.questionnaire.v3 import Questionnaire
from domain.repository.errors import ItemNotFound

PATH_TO_QUESTIONNAIRES = Path(__file__).parent / "questionnaires"


def version_from_file_path(file_path: Path) -> int:
    return int(file_path.stem.lstrip("v"))


def get_latest_schema_path_by_name(name: str) -> Path | None:
    possible_paths = PATH_TO_QUESTIONNAIRES.glob(f"{name}/v*.json")
    paths_sorted_by_version = sorted(possible_paths, key=version_from_file_path)
    try:
        path = paths_sorted_by_version[-1]
    except IndexError:
        path = None
    return path


def read_schema(path: Path) -> str:
    with open(path, "r") as fp:
        return fp.read()


class QuestionnaireRepository:

    def read(self, name: str) -> Questionnaire:
        path = get_latest_schema_path_by_name(name=name)
        if not path:
            raise ItemNotFound(name, item_type=Questionnaire)
        version = version_from_file_path(path)
        schema = read_schema(path=path)
        return Questionnaire(name=name, version=version, json_schema=schema)
