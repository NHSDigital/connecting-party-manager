from enum import Enum, StrEnum, auto

from pydantic import BaseModel


class IssueType(StrEnum):
    # https://simplifier.net/packages/hl7.fhir.r4.core/4.0.1/files/83603/~json
    PROCESSING = "processing"
    INFORMATIONAL = "informational"


class IssueSeverity(StrEnum):
    # https://build.fhir.org/valueset-issue-severity.html
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


class Coding(BaseModel):
    code: str
    display: str


class SpineCoding(StrEnum):

    @staticmethod
    def _generate_next_value_(name: str, *args):
        """Change default behaviour to generate capitalised values"""
        return name.upper()

    VALIDATION_ERROR = auto()
    UNPROCESSABLE_ENTITY = auto()
    MISSING_VALUE = auto()
    ACCESS_DENIED = auto()
    SERVICE_ERROR = auto()
    SERVICE_UNAVAILABLE = auto()
    RESOURCE_NOT_FOUND = auto()


class CpmCoding(Enum):
    OK = Coding(code="OK", display="Transaction successful")
    RESOURCE_CREATED = Coding(code="RESOURCE_CREATED", display="Resource created")

    @property
    def value(self):
        return self._value_.dict(exclude_none=True)
