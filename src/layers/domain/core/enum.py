from enum import StrEnum, auto


class Status(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()  # "soft" delete


class Environment(StrEnum):
    DEV = auto()
    QA = auto()
    REF = auto()
    INT = auto()
    PROD = auto()
