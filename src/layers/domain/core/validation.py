import re

UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ODS_CODE_REGEX = r"^[a-zA-Z0-9]{1,5}$"
ENTITY_NAME_REGEX = r"^\S+( \S+)*$"
ACCREDITED_SYSTEM_ID_REGEX = re.compile(r"^[0-9]{1,12}$")
DEVICE_NAME_REGEX = (
    r"^[a-zA-Z]{1}[ -~]+$"  # starts with any letter, followed by any sequence of ascii
)
