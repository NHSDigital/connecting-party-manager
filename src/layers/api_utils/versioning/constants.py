import re

VERSION_RE = re.compile(r"^v(\d+)$")


class VersioningStepArgs:
    VERSIONED_STEPS = "versioned_steps"
    EVENT = "event"
