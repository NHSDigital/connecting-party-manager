import re

VERSION_HEADER_PATTERN = r"^(\d+)$"
VERSION_RE = re.compile(r"^v(\d+)$")


class VERSIONING_STEP_ARGS:
    VERSIONED_STEPS = "versioned_steps"
    EVENT = "event"
