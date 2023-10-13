import re

NON_CAPS_RE = re.compile(r"[^a-zA-Z0-9]")
SEPARATOR = "-"
DOUBLE_SEPARATOR = f"{SEPARATOR}{SEPARATOR}"


def make_log_reference(name):
    stripped_name = NON_CAPS_RE.sub(SEPARATOR, name)
    while DOUBLE_SEPARATOR in stripped_name:
        stripped_name = stripped_name.replace(DOUBLE_SEPARATOR, SEPARATOR)
    return stripped_name.upper()
