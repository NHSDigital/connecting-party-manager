from enum import StrEnum

from .v1 import TableKeyAction


class TableKey(TableKeyAction, StrEnum):
    DEVICE = "D"
    DEVICE_TAG = "DT"
