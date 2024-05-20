from enum import StrEnum, auto

FILTER_TERMS = [
    ("objectClass", "nhsMHS"),
    ("objectClass", "nhsAS"),
    ("objectClass", "delete"),
    ("objectClass", "modify"),
]


class CaseInsensitiveEnum(StrEnum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member == value:
                    return member
        return None


class ChangeType(CaseInsensitiveEnum):
    ADD = auto()
    MODIFY = auto()
    DELETE = auto()


class InteractionType(CaseInsensitiveEnum):
    FHIR = auto()
    HL7 = auto()
    EBXML = auto()
    NA = "N/A"
    MSHSIGNALSONLY = auto()  # a bug?


class YesNoAnswer(CaseInsensitiveEnum):
    ALWAYS = auto()  # "yes"
    NEVER = auto()  # "no"


class Authentication(CaseInsensitiveEnum):
    NONE = auto()
    TRANSIENT = auto()
    PERSISTENT = auto()


class SyncReplyModel(CaseInsensitiveEnum):
    MSHSIGNALSONLY = auto()
    NEVER = auto()
    NONE = auto()
    SIGNALSANDRESPONSE = auto()


class MhsActor(CaseInsensitiveEnum):
    TOPARTYMSH = "urn:oasis:names:tc:ebxml-msg:actor:topartymsh"
    NEXTMSH = "urn:oasis:names:tc:ebxml-msg:actor:nextmsh"
    IGNORED = "IGNORED"


class ChangeType(CaseInsensitiveEnum):
    ADD = auto()
    MODIFY = auto()
    DELETE = auto()


class OrganizationalUnitServices(CaseInsensitiveEnum):
    SERVICES = auto()


class OrganizationalUnitNhs(CaseInsensitiveEnum):
    NHS = auto()


class ChangelogCommonName(CaseInsensitiveEnum):
    CHANGELOG = auto()


class ModificationType(CaseInsensitiveEnum):
    ADD = auto()
    REPLACE = auto()
    DELETE = auto()
