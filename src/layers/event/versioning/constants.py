import re

VERSION_RE = re.compile(r"^v(\d+)$")


class VERSIONING_STEP_ARGS:
    VERSIONED_STEPS = "versioned_steps"
    EVENT = "event"
