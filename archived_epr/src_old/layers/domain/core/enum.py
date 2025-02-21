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


class EntityType(StrEnum):
    PRODUCT_TEAM = auto()
    PRODUCT_TEAM_ALIAS = auto()
    PRODUCT = auto()
