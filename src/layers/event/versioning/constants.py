import re

VERSION_HEADER_PATTERN = r"^(\d+)$"
VERSION_RE = re.compile(r"^v(\d+)$")
API_ROOT_DIRNAME = "src/api"
VERSIONED_HANDLER_GLOB = "src/v*/steps.py"
