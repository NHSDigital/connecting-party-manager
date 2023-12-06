from enum import StrEnum


class TableKeys(StrEnum):
    PRODUCT_TEAM = "T"
    DEVICE = "D"
    DEVICE_KEY = "DK"
    DEVICE_PAGE = "DP"
    DEVICE_RELATIONSHIP = "DR"
    ODS_ORGANISATION = "O"


def product_team_pk(id):
    return f"{TableKeys.PRODUCT_TEAM._value_}#{id}"


def device_pk(id):
    return f"{TableKeys.DEVICE._value_}#{id}"


def device_key_sk(key):
    return f"{TableKeys.DEVICE_KEY._value_}#{key}"


def device_page_sk(page):
    return f"{TableKeys.DEVICE_PAGE._value_}#{page}"


def device_relationship_sk(target_id):
    return f"{TableKeys.DEVICE_RELATIONSHIP._value_}#{target_id}"


def ods_pk(ods_code):
    return f"{TableKeys.ODS_ORGANISATION._value_}#{ods_code}"
