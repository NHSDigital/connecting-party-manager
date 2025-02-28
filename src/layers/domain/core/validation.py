import re

_ODS_CODE_REGEX = r"[a-zA-Z0-9]{1,9}"
UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ODS_CODE_REGEX = rf"^({_ODS_CODE_REGEX})$"
ENTITY_NAME_REGEX = r"^\S+( \S+)*$"
CPM_PRODUCT_NAME_REGEX = r"^[ -~]+$"  # any sequence of ascii


class CpmId:
    class Product:
        PRODUCT_ID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"
        ID_PATTERN = re.compile(
            rf"^P\.[{PRODUCT_ID_CHARS}]{{3}}-[{PRODUCT_ID_CHARS}]{{3}}$"
        )

    class ProductTeamIdAlias:
        ID_PATTERN = re.compile(rf"^[ -~]+$")

    class General:
        ID_PATTERN = re.compile(rf"^[a-zA-Z0-9]+$")
