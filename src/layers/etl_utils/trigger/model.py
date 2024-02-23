import json
from datetime import datetime as dt
from typing import Literal, Self

from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from event.environment import BaseEnvironment
from pydantic import BaseModel, Field

NAME_SEPARATOR = "."
BAD_CHARACTERS = [" ", ":"]
BULK_CHANGELOG_NUMBER = "0"


def _create_timestamp() -> str:
    return dt.now().isoformat()


class StateMachineInput(BaseModel):
    init: WorkerKey
    changelog_number: str
    name_: Literal["bulk", "changelog", "retry"]
    timestamp: str = Field(default_factory=_create_timestamp)

    @classmethod
    def bulk(cls) -> Self:
        return cls(
            init=WorkerKey.EXTRACT, changelog_number=BULK_CHANGELOG_NUMBER, name_="bulk"
        )

    @classmethod
    def changelog(cls, changelog_number: str) -> Self:
        return cls(
            init=WorkerKey.EXTRACT, changelog_number=changelog_number, name_="changelog"
        )

    def dict(self):
        changelog_number = self.changelog_number or json.dumps(None)
        return {"init": self.init.name.lower(), CHANGELOG_NUMBER: changelog_number}

    @property
    def name(self) -> str:
        state_machine_name = ".".join(
            (self.name_, self.init.name, self.changelog_number, self.timestamp)
        )

        for char in BAD_CHARACTERS:
            state_machine_name = state_machine_name.replace(char, NAME_SEPARATOR)
        return state_machine_name


class TriggerEnvironment(BaseEnvironment):
    STATE_MACHINE_ARN: str
    NOTIFY_LAMBDA_ARN: str
    TABLE_NAME: str
