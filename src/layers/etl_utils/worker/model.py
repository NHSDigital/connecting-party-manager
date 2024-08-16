from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Optional

from event.environment import BaseEnvironment
from pydantic import BaseModel


class WorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"


class EtlType(StrEnum):
    BULK = auto()
    UPDATES = auto()


class WorkerEvent(BaseModel):
    max_records: Optional[int] = None
    etl_type: EtlType = None


@dataclass
class WorkerResponse:
    """The response of an ETL worker lambda"""

    stage_name: str
    processed_records: int
    unprocessed_records: int
    error_message: None | str


@dataclass
class WorkerActionResponse:
    """The response on an ETL worker lambda's action"""

    unprocessed_records: deque[dict]
    processed_records: deque[dict]
    s3_input_path: str
    exception: Exception | None
    s3_output_path: str | None = field(default=None)
