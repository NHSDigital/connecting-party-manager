from string import printable, whitespace
from unittest import mock

import pytest
from domain.core.error import (
    BadAsidError,
    BadEntityNameError,
    BadProductIdError,
    BadUuidError,
    InvalidOdsCodeError,
    InvalidTypeError,
)
from domain.core.validation import (
    ASID_REGEX,
    PRODUCT_ID_REGEX,
    UUID_REGEX,
    validate_asid,
    validate_entity_name,
    validate_ods_code,
    validate_product_id,
    validate_type,
    validate_uuid,
)
from hypothesis import given
from hypothesis.strategies import from_regex, text


@given(uuid=from_regex(UUID_REGEX))
def test_validate_uuid_success(uuid: str):
    validate_uuid(uuid=uuid)


@given(uuid=from_regex(PRODUCT_ID_REGEX))  # NB: wrong regex pattern
def test_validate_uuid_fail(uuid: str):
    with pytest.raises(BadUuidError):
        validate_uuid(uuid=uuid)


@given(asid=from_regex(ASID_REGEX))
def test_validate_asid_success(asid: str):
    validate_asid(asid=asid)


@given(asid=from_regex(UUID_REGEX))  # NB: wrong regex pattern
def test_validate_asid_fail(asid: str):
    with pytest.raises(BadAsidError):
        validate_asid(asid=asid)


@given(product_id=from_regex(PRODUCT_ID_REGEX))
def test_validate_product_id_success(product_id: str):
    validate_product_id(product_id=product_id)


@given(product_id=from_regex(ASID_REGEX))  # NB: wrong regex pattern
def test_validate_product_id_fail(product_id: str):
    with pytest.raises(BadProductIdError):
        validate_product_id(product_id=product_id)


@given(name=text(alphabet=set(printable) - set(whitespace), min_size=1, max_size=5))
def test_validate_entity_name_success(name):
    validate_entity_name(name=name)


@given(name=text(alphabet=whitespace, max_size=5))
def test_validate_entity_name_fail(name):
    with pytest.raises(BadEntityNameError):
        validate_entity_name(name=name)


class MyObject:
    pass


@pytest.mark.parametrize("obj_type", (str, bool, Exception, dict, object, MyObject))
def test_validate_type_pass(obj_type: type):
    validate_type(obj=obj_type(), expected_type=obj_type)


@pytest.mark.parametrize("obj_type", (str, bool, Exception, dict, object, MyObject))
def test_validate_type_fail(obj_type: type):
    with pytest.raises(InvalidTypeError):
        validate_type(obj=list(), expected_type=obj_type)


@mock.patch("domain.core.validation.is_valid_ods_code", return_value=True)
def test_validate_ods_code_pass(mocked_is_valid_ods_code):
    validate_ods_code("")


@mock.patch("domain.core.validation.is_valid_ods_code", return_value=False)
def test_validate_ods_code_pass(mocked_is_valid_ods_code):
    with pytest.raises(InvalidOdsCodeError):
        validate_ods_code("")
