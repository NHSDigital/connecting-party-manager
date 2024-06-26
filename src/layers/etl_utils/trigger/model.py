import datetime
import json
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self

from pydantic import BaseModel, Field

NAME_SEPARATOR = "."
BAD_CHARACTERS = [" ", ":"]


def _create_timestamp() -> str:
    return datetime.datetime.now().isoformat()


class StateMachineInputType(StrEnum):
    BULK = auto()
    UPDATE = auto()


@dataclass
class TriggerResponse:
    """The response of an ETL trigger lambda"""

    message: str
    error_message: None | str


class StateMachineInput(BaseModel):
    etl_type: StateMachineInputType
    changelog_number_start: int
    changelog_number_end: int
    timestamp: str = Field(default_factory=_create_timestamp)

    @classmethod
    def bulk(cls, changelog_number: int) -> Self:
        return cls(
            etl_type=StateMachineInputType.BULK,
            changelog_number_start=0,
            changelog_number_end=changelog_number,
        )

    @classmethod
    def update(cls, changelog_number_start: int, changelog_number_end: int) -> Self:
        return cls(
            etl_type=StateMachineInputType.UPDATE,
            changelog_number_start=changelog_number_start,
            changelog_number_end=changelog_number_end,
        )

    @property
    def name(self) -> str:
        state_machine_name = NAME_SEPARATOR.join(
            (
                self.etl_type,
                str(self.changelog_number_start),
                str(self.changelog_number_end),
                self.timestamp,
            )
        )
        for char in BAD_CHARACTERS:
            state_machine_name = state_machine_name.replace(char, NAME_SEPARATOR)
        return state_machine_name

    def json_with_name(self) -> str:
        data = self.dict()
        data["name"] = self.name
        return json.dumps(data)
