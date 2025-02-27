from enum import StrEnum

EXCEPTIONAL_ODS_CODES = {
    "696B001",
    "TESTEBS1",
    "TESTLSP0",
    "TESTLSP1",
    "TESTLSP3",
    "TMSAsync1",
    "TMSAsync2",
    "TMSAsync3",
    "TMSAsync4",
    "TMSAsync5",
    "TMSAsync6",
    "TMSEbs2",
    "SPINE",
}

BAD_UNIQUE_IDENTIFIERS = {
    "31af51067f47f1244d38",  # pragma: allowlist secret
    "a83e1431f26461894465",  # pragma: allowlist secret
    "S2202584A2577603",
    "S100049A300185",
}


class SdsFieldName(StrEnum):
    ODS_CODE = "ODS Code"
    ASID = "ASID"
    CPA_ID = "MHS CPA ID"
    MHS_FQDN = "MHS FQDN"
    ADDRESS = "Address"
    PARTY_KEY = "MHS Party Key"
    MANAGING_ORGANIZATION = "Managing Organization"
    DATE_REQUESTED = "Date Requested"
    DATE_APPROVED = "Date Approved"
    DATE_DNS_APPROVED = "Date DNS Approved"
    MHS_SN = "MHS SN"
    MHS_IN = "MHS IN"
    INTERACTION_ID = "Interaction ID"
    UNIQUE_IDENTIFIER = "Unique Identifier"
    MANUFACTURING_ORG = "MHS Manufacturer Organisation"
    PRODUCT_KEY = "Product Key"
    CLIENT_ODS_CODES = "Client ODS Codes"
    TEMP_UID = "Temp UID"


CPM_MHS_IMMUTABLE_FIELDS = {
    SdsFieldName.MANUFACTURING_ORG,
    SdsFieldName.PARTY_KEY,
    SdsFieldName.CPA_ID,
    SdsFieldName.UNIQUE_IDENTIFIER,
}

CPM_ACCREDITED_SYSTEM_IMMUTABLE_FIELDS = {
    SdsFieldName.MANUFACTURING_ORG,
    SdsFieldName.PARTY_KEY,
    SdsFieldName.ASID,
}


class SdsDeviceReferenceDataPath(StrEnum):
    ALL = "*"
    ALL_INTERACTION_IDS = f"*.{SdsFieldName.INTERACTION_ID}"


MESSAGE_SETS_SUFFIX = "MHS Message Sets"
ADDITIONAL_INTERACTIONS_SUFFIX = "AS Additional Interactions"
MHS_DEVICE_SUFFIX = "Message Handling System"
AS_DEVICE_SUFFIX = "Accredited System"
PRODUCT_TEAM_PREFIX = "EPR-"


class EprNameTemplate(StrEnum):
    PRODUCT_TEAM = "{ods_code} (EPR)"
    PRODUCT_TEAM_KEY = f"{PRODUCT_TEAM_PREFIX}{{ods_code}}"
    ADDITIONAL_INTERACTIONS = f"{{party_key}} - {ADDITIONAL_INTERACTIONS_SUFFIX}"
    MESSAGE_SETS = f"{{party_key}} - {MESSAGE_SETS_SUFFIX}"
    MHS_DEVICE = f"{{party_key}} - {MHS_DEVICE_SUFFIX}"
    AS_DEVICE = f"{{party_key}}/{{asid}} - {AS_DEVICE_SUFFIX}"


class ModificationType(StrEnum):
    ADD = "Add"
    REPLACE = "Replace"
    DELETE = "Delete"
