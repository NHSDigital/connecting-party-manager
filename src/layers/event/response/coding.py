from enum import Enum, StrEnum

from domain.fhir.r4 import Coding

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


class PydanticModelEnum(Enum):
    @property
    def value(self):
        return self._value_.dict(exclude_none=True)


class FhirCoding(PydanticModelEnum):
    VALIDATION_ERROR = Coding(
        code="VALIDATION_ERROR",
        display="Validation error",
        system=CODE_SYSTEM,
    )
    UNPROCESSABLE_ENTITY = Coding(  # NB: doesn't yet exist
        code="UNPROCESSABLE_ENTITY",
        display="A required resource was not available",
        system=CODE_SYSTEM,
    )
    MISSING_VALUE = Coding(
        code="MISSING_VALUE",
        display="Missing value",
        system=CODE_SYSTEM,
    )
    ACCESS_DENIED = Coding(
        code="ACCESS_DENIED",
        display="Access has been denied to process this request",
        system=CODE_SYSTEM,
    )
    SERVICE_ERROR = Coding(
        code="SERVICE_ERROR",
        display="Service error",
        system=CODE_SYSTEM,
    )
    RESOURCE_NOT_FOUND = Coding(
        code="RESOURCE_NOT_FOUND",
        display="Resource not found",
        system=CODE_SYSTEM,
    )


class CpmCoding(PydanticModelEnum):
    OK = Coding(
        code="OK",
        display="Transaction successful",
        system=CODE_SYSTEM,
    )
    RESOURCE_CREATED = Coding(
        code="RESOURCE_CREATED",
        display="Resource created",
        system=CODE_SYSTEM,
    )
