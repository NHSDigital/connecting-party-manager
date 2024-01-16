from dataclasses import dataclass

from event.environment import BaseEnvironment


class WorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str


@dataclass
class WorkerResponse:
    stage_name: str
    count_processed: int
    count_unprocessed: int
    error_message: None | str
