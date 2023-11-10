from enum import StrEnum


class TableKeys(StrEnum):
    PRODUCT_TEAM = "T"
    PRODUCT = "P"
    PRODUCT_KEY = "PK"
    PRODUCT_RELATIONSHIP = "PR"
    ODS_ORGANISATION = "O"


def product_team_pk(id):
    return f"{TableKeys.PRODUCT_TEAM._value_}#{id}"


def product_pk(id):
    return f"{TableKeys.PRODUCT._value_}#{id}"


def product_key_sk(key):
    return f"{TableKeys.PRODUCT_KEY._value_}#{key}"


def product_relationship_sk(target_id):
    return f"{TableKeys.PRODUCT_RELATIONSHIP._value_}#{target_id}"


def ods_pk(ods_code):
    return f"{TableKeys.ODS_ORGANISATION._value_}#{ods_code}"
