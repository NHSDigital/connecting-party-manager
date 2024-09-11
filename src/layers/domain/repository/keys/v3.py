from enum import StrEnum

from .v1 import TableKeyAction


class TableKey(TableKeyAction, StrEnum):
    CPM_SYSTEM_ID = "CSI"
