import re
from uuid import UUID

from domain.core.error import (
    BadAsidError,
    BadEntityNameError,
    BadProductIdError,
    BadProductIdOrAsidError,
    BadUuidError,
    InvalidOdsCodeError,
    InvalidTypeError,
)
from domain.ods import is_valid_ods_code

UUID_REGEX = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ASID_REGEX = re.compile(r"^[0-9]{1,12}$")
PRODUCT_ID_REGEX = re.compile(r"^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$")


def _validate_with_regex(value: str, regex: re.Pattern, exception: Exception):
    if not regex.match(value):
        raise exception


def validate_uuid(uuid: UUID | str):
    _validate_with_regex(
        value=str(uuid),
        regex=UUID_REGEX,
        exception=BadUuidError(f"UUID required: {uuid}"),
    )


def validate_asid(asid: str):
    _validate_with_regex(
        value=asid, regex=ASID_REGEX, exception=BadAsidError(f"ASID required: {asid}")
    )


def validate_product_id(product_id: str):
    _validate_with_regex(
        value=product_id,
        regex=PRODUCT_ID_REGEX,
        exception=BadProductIdError(f"Product Id required: {product_id}"),
    )


def validate_product_id_or_asid(id: str):
    for validator in (validate_product_id, validate_asid):
        try:
            return validator(id)
        except BadProductIdOrAsidError.EXCEPTION_GROUP:
            pass
    raise BadProductIdOrAsidError(id=id)


def validate_entity_name(name: str):
    if name.strip() == "":
        raise BadEntityNameError(f"Invalid name: {name}")


def validate_type(obj: any, expected_type: type):
    if type(obj) is not expected_type:
        raise InvalidTypeError(f"Expected '{obj}' to be of type '{expected_type}'")


def validate_ods_code(ods_code: str):
    if not is_valid_ods_code(ods_code=ods_code):
        raise InvalidOdsCodeError(f"Invalid ODS Code: {ods_code}")
