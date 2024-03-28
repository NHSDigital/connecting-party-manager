from collections import deque
from enum import StrEnum

CHANGELOG_NUMBER = "changelog-number"
CHANGELOG_QUERY = "{}"
EMPTY_LDIF = ""
EMPTY_ARRAY = deque()
LDIF_RECORD_DELIMITER = "\n\n"


class WorkerKey(StrEnum):
    EXTRACT = "input--extract/unprocessed"
    TRANSFORM = "input--transform/unprocessed"
    LOAD = "input--load/unprocessed"
