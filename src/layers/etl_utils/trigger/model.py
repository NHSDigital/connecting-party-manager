import json
from datetime import datetime as dt
from enum import StrEnum, auto
from typing import Self

from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from event.environment import BaseEnvironment
from pydantic import BaseModel, Field

NAME_SEPARATOR = "."
BAD_CHARACTERS = [" ", ":"]


def _create_timestamp() -> str:
    return dt.now().isoformat()


class StateMachineInputType(StrEnum):
    BULK = auto()
    UPDATE = auto()
    RETRY = auto()


class StateMachineInput(BaseModel):
    init: WorkerKey
    changelog_number_start: int
    changelog_number_end: int
    name_: StateMachineInputType
    timestamp: str = Field(default_factory=_create_timestamp)

    @classmethod
    def bulk(cls, changelog_number: int) -> Self:
        return cls(
            init=WorkerKey.EXTRACT,
            changelog_number_start=0,
            changelog_number_end=changelog_number,
            name_=StateMachineInputType.BULK,
        )

    @classmethod
    def update(cls, changelog_number_start: int, changelog_number_end: int) -> Self:
        return cls(
            init=WorkerKey.EXTRACT,
            changelog_number_start=changelog_number_start,
            changelog_number_end=changelog_number_end,
            name_=StateMachineInputType.UPDATE,
        )

    def dict(self):
        changelog_number = self.changelog_number_end or json.dumps(None)
        return {"init": self.init.name.lower(), CHANGELOG_NUMBER: changelog_number}

    @property
    def name(self) -> str:
        state_machine_name = ".".join(
            (
                self.name_,
                self.init.name,
                str(self.changelog_number_start),
                str(self.changelog_number_end),
                self.timestamp,
            )
        )

        for char in BAD_CHARACTERS:
            state_machine_name = state_machine_name.replace(char, NAME_SEPARATOR)
        return state_machine_name


class TriggerEnvironment(BaseEnvironment):
    STATE_MACHINE_ARN: str
    NOTIFY_LAMBDA_ARN: str
    TABLE_NAME: str
