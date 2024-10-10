from enum import StrEnum

from .v1 import TableKeyAction


class TableKey(TableKeyAction, StrEnum):
    PRODUCT_TEAM = "PT"
    PRODUCT_TEAM_KEY = "PTK"
    CPM_SYSTEM_ID = "CSI"
    CPM_PRODUCT = "P"
    CPM_PRODUCT_KEY = "PK"
    CPM_PRODUCT_STATUS = "PS"
