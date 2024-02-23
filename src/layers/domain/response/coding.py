from enum import Enum, StrEnum
from typing import Literal

from domain.fhir.r4 import Coding as _Coding

CODE_SYSTEM = "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"


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


class Coding(_Coding):
    system: Literal[
        "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
    ] = CODE_SYSTEM


class PydanticModelEnum(Enum):
    @property
    def value(self):
        return self._value_.dict(exclude_none=True)


class FhirCoding(PydanticModelEnum):
    VALIDATION_ERROR = Coding(code="VALIDATION_ERROR", display="Validation error")
    UNPROCESSABLE_ENTITY = Coding(  # NB: doesn't yet exist
        code="UNPROCESSABLE_ENTITY", display="A required resource was not available"
    )
    MISSING_VALUE = Coding(code="MISSING_VALUE", display="Missing value")
    ACCESS_DENIED = Coding(
        code="ACCESS_DENIED", display="Access has been denied to process this request"
    )
    SERVICE_ERROR = Coding(code="SERVICE_ERROR", display="Service error")
    SERVICE_UNAVAILABLE = Coding(
        code="SERVICE_UNAVAILABLE", display="Service unavailable - could be temporary"
    )
    RESOURCE_NOT_FOUND = Coding(code="RESOURCE_NOT_FOUND", display="Resource not found")


class CpmCoding(PydanticModelEnum):
    OK = Coding(code="OK", display="Transaction successful")
    RESOURCE_CREATED = Coding(code="RESOURCE_CREATED", display="Resource created")
