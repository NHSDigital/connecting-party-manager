from enum import StrEnum, auto


class Status(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()  # "soft" delete
