import re
from typing import Iterable, TypeVar

UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
ODS_CODE_REGEX = r"^[0-9A-Z]{1,5}$"
ASID_REGEX = r"^[0-9]{1,12}$"
PRODUCT_ID_REGEX = r"^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$"
INT_REGEX = r"^-?[0-9]+$"

T = TypeVar("T")


def default_set(iterable: Iterable[T]) -> set[T]:
    return set(iterable if iterable is not None else [])


def assert_is_uuid(value: str):
    assert re.match(UUID_REGEX, value), f"UUID required: {value}"


def assert_is_ods_code(value: str):
    assert re.match(ODS_CODE_REGEX, value), f"ODS Code required: {value}"


def assert_is_asid(value: str):
    assert re.match(ASID_REGEX, value), f"ASID required: {value}"


def assert_is_product_id(value: str):
    assert re.match(PRODUCT_ID_REGEX, value), f"Product Id required: {value}"
