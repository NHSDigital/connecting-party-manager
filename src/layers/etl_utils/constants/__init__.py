from enum import StrEnum

CHANGELOG_NUMBER = "changelog-number"


class WorkerKey(StrEnum):
    EXTRACT = "input--extract/unprocessed"
    TRANSFORM = "input--transform/unprocessed"
    LOAD = "input--load/unprocessed"
