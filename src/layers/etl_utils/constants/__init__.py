from enum import StrEnum


class WorkerKey(StrEnum):
    EXTRACT = "input--extract/unprocessed"
    TRANSFORM = "input--transform/unprocessed"
