from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, FilePath


class LogInfoTemplate(BaseModel):
    level: Literal["INFO", "DEBUG", "WARNING", "ERROR"]
    path: FilePath
    line_no: int
    func: str
    pid: int
    thread: int


class LogTemplate(BaseModel):
    timestamp: float
    log_reference: str = (Field(pattern=r"^[A-Z]+$"),)
    internal_id: str = Field(pattern=r"^[a-z0-9]{32}+$")
    action: str
    action_duration: float
    action_status: Literal["succeeded", "failed", "error"]
    action_result: Optional[Any] = None
    log_info: LogInfoTemplate


class StepLog(LogTemplate):
    data: dict
    cache: dict
    result: Any
