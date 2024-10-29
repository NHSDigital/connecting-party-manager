from enum import StrEnum, auto


class QuestionnaireInstance(StrEnum):
    SPINE_AS = auto()
    SPINE_MHS = auto()
    SPINE_AS_ADDITIONAL_INTERACTIONS = auto()
    SPINE_MHS_MESSAGE_SETS = auto()
