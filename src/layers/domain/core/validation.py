import re

DEVICE_KEY_SEPARATOR = ":"

_ODS_CODE_REGEX = r"[a-zA-Z0-9]{1,9}"
UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ODS_CODE_REGEX = rf"^({_ODS_CODE_REGEX})$"
ENTITY_NAME_REGEX = r"^\S+( \S+)*$"
DEVICE_NAME_REGEX = r"^[ -~]+$"  # any sequence of ascii
CPM_PRODUCT_NAME_REGEX = r"^[ -~]+$"  # any sequence of ascii


class CpmId:
    class Product:
        PRODUCT_ID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"
        ID_PATTERN = re.compile(
            rf"^P\.[{PRODUCT_ID_CHARS}]{{3}}-[{PRODUCT_ID_CHARS}]{{3}}$"
        )


class SdsId:
    class AccreditedSystem:
        ID_PATTERN = re.compile(
            rf"^({_ODS_CODE_REGEX}){DEVICE_KEY_SEPARATOR}[a-zA-Z-0-9]+$"
        )

    class MessageHandlingSystem:
        INTERACTION_ID_REGEX = r"[a-zA-Z-0-9_:\-\.\/?=]+"
        PARTY_KEY_REGEX = rf"{_ODS_CODE_REGEX}-[0-9]{{1,12}}"
        ID_PATTERN = re.compile(
            rf"^{_ODS_CODE_REGEX}{DEVICE_KEY_SEPARATOR}{PARTY_KEY_REGEX}{DEVICE_KEY_SEPARATOR}{INTERACTION_ID_REGEX}$"
        )
