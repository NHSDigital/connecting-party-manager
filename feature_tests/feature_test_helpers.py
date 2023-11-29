from enum import StrEnum, auto

from behave.configuration import Configuration


class TestMode(StrEnum):
    LOCAL = auto()
    INTEGRATION = auto()

    def parse(config: Configuration) -> "TestMode":
        test_mode = config.userdata.get("test_mode", TestMode.LOCAL)
        return TestMode(test_mode)
