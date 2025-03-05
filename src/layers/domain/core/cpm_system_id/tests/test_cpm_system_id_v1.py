import os
from pathlib import Path

import pytest
from domain.core.cpm_system_id import PRODUCT_TEAM_ID_PATTERN, ProductId, ProductTeamId
from event.json import json_load

PATH_TO_CPM_SYSTEM_IDS = Path(__file__).parent.parent
PRODUCT_IDS_GENERATED_FILE = f"{PATH_TO_CPM_SYSTEM_IDS}/generated_ids/product_ids.json"
generated_product_ids = set()


@pytest.fixture(scope="module")
def _get_generated_ids():
    global generated_product_ids
    if os.path.exists(PRODUCT_IDS_GENERATED_FILE):
        with open(PRODUCT_IDS_GENERATED_FILE, "r") as file:
            generated_product_ids = set(json_load(file))


def test_cpm_product_team_id_generator():
    generator = ProductTeamId.create()
    assert PRODUCT_TEAM_ID_PATTERN.match(generator.id)


def test_cpm_product_tema_id_validate_id_valid():
    valid_key = "3150ac97-45d0-40f6-904f-c6422c46e711"
    is_valid = ProductTeamId.validate(valid_key)
    assert is_valid


@pytest.mark.repeat(50)
def test_product_id_generator_format_key(_get_generated_ids):
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
