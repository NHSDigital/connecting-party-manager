import os
from pathlib import Path

import pytest
from domain.core.cpm_system_id import AsidId, PartyKeyId, ProductId
from event.json import json_load

PATH_TO_CPM_SYSTEM_IDS = Path(__file__).parent.parent
PRODUCT_IDS_GENERATED_FILE = f"{PATH_TO_CPM_SYSTEM_IDS}/generated_ids/product_ids.json"
generated_product_ids = set()


@pytest.fixture(scope="module", autouse=True)
def _get_generated_ids():
    global generated_product_ids
    if os.path.exists(PRODUCT_IDS_GENERATED_FILE):
        with open(PRODUCT_IDS_GENERATED_FILE, "r") as file:
            generated_product_ids = set(json_load(file))


def test_party_key_generator_format_key():
    generator = PartyKeyId.create(current_number=123456, ods_code="ABC")
    expected_key = "ABC-123457"  # Expecting the number to be formatted with 6 digits
    assert generator.id == expected_key


def test_party_key_generator_validate_key_valid():
    valid_key = "ABC-123457"
    is_valid = PartyKeyId.validate_cpm_system_id(valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "ABC000124",  # Missing hyphen
        "ABC-1234",  # Number part too short
        "ABC-1234567",  # Number part too long
        "ABC-0001A4",  # Number part contains a non-digit character
        "",  # Empty string
    ],
)
def test_party_key_generator_validate_key_invalid_format(invalid_key):
    is_valid = PartyKeyId.validate_cpm_system_id(invalid_key)
    assert not is_valid


def test_party_key_generator_increment_number():
    # Test that the number is incremented correctly
    generator = PartyKeyId.create(current_number=123456, ods_code="XYZ")
    expected_key = "XYZ-123457"  # Expecting increment from 123456 to 123457
    assert generator.id == expected_key


def test_asid_generator_validate_key_valid():
    valid_key = "223456789014"
    is_valid = AsidId.validate_cpm_system_id(valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "1234567890123",
        "12345678901",
        "1234567890",
        "123456789",
        "12345678",
        "1234567",
        "123456",
        "12345",
        "1234",
        "123",
        "12",
        "1",
        "",  # Empty string
    ],
)
def test_asid_generator_validate_key_invalid_format(invalid_key):
    is_valid = AsidId.validate_cpm_system_id(invalid_key)
    assert not is_valid


def test_asid_generator_increment_number():
    # Test that the number is incremented correctly
    generator = AsidId.create(current_number=223456789012)
    assert generator.id == "223456789013"


@pytest.mark.repeat(50)
def test_product_id_generator_format_key():
    generator = ProductId.create()
    assert generator.id is not None
    assert generator.id not in generated_product_ids


@pytest.mark.parametrize(
    "valid_key",
    [
        "P.AAA-333",
        "P.AC3-333",
        "P.ACC-33A",
    ],
)
def test_product_id_generator_validate_key_valid(valid_key):
    is_valid = ProductId.validate_cpm_system_id(cpm_system_id=valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "P.BBB-111",  # Invalid characters
        "AAC346",  # Missing 'P.' and hyphen
        "P-ACD-333",  # Extra hyphen
        "P.ACC344",  # Missing hyphen
        "P.ACC-3467",  # Too many digits
        "P.AAC-34",  # Too few digits
        "",  # Empty string
    ],
)
def test_product_id_generator_validate_key_invalid_format(invalid_key):
    is_valid = ProductId.validate_cpm_system_id(cpm_system_id=invalid_key)
    assert not is_valid
