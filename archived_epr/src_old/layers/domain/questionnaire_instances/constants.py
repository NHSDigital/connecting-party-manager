from enum import StrEnum, auto
from pathlib import Path

PATH_TO_QUESTIONNAIRES = Path(__file__).parent / "questionnaires"


class QuestionnaireInstance(StrEnum):
    SPINE_AS = auto()
    SPINE_MHS = auto()
    SPINE_AS_ADDITIONAL_INTERACTIONS = auto()
    SPINE_MHS_MESSAGE_SETS = auto()
