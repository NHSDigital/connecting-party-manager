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


class SdsFieldName(StrEnum):
    ASID = "ASID"
    CPA_ID = "MHS CPA ID"
    MHS_FQDN = "MHS FQDN"
    ADDRESS = "Address"
    PARTY_KEY = "MHS Party key"
    MANAGING_ORGANIZATION = "Managing Organization"
    DATE_REQUESTED = "Date Requested"
    DATE_APPROVED = "Date Approved"
    DATE_DNS_APPROVED = "Date DNS Approved"
    MHS_SN = "MHS SN"
    MHS_IN = "MHS IN"
    INTERACTION_ID = "Interaction ID"
    UNIQUE_IDENTIFIER = "Unique Identifier"


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
