from dataclasses import dataclass

from behave.model import Table
from behave.runner import Context as BehaveContext
from requests import Response


@dataclass
class Context(BehaveContext):
    base_url: str
    headers: dict[str, dict[str, str]] = None
    response: Response = None
    table: Table = None
