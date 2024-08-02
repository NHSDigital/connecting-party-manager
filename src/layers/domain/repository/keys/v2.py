from enum import StrEnum

from .v1 import TableKeyAction


class TableKey(StrEnum, TableKeyAction):
    DEVICE = "D"
    DEVICE_TAG = "DT"
