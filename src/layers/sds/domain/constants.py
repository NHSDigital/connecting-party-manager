from enum import StrEnum, auto


class CaseInsensitiveEnum(StrEnum):
    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member == value:
                return member
        return None


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
    TOPARTHMSH = "urn:oasis:names:tc:ebxml-msg:actor:topartymsh"
    NEXTMSH = "urn:oasis:names:tc:ebxml-msg:actor:nextmsh"


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
