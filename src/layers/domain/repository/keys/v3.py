from enum import StrEnum

from .v1 import TableKeyAction


class TableKey(TableKeyAction, StrEnum):
    PRODUCT_TEAM = "PT"
    CPM_SYSTEM_ID = "CSI"
    CPM_PRODUCT = "P"
    CPM_PRODUCT_KEY = "PK"
