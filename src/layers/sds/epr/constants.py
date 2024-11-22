from enum import StrEnum


class SdsFieldName(StrEnum):
    INTERACTION_ID = "Interaction ID"
    ASID = "ASID"


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
