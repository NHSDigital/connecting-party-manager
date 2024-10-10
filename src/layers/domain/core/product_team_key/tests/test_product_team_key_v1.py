import pytest
from domain.core.product_team_key.v1 import ProductTeamKeyType, validate_key

GOOD_ID_EXAMPLES = {
    "product_team_id_alias": "FOOBAR",
}

BAD_ID_EXAMPLES = {
    "product_team_id": "FOOBAR",
    "foo": "BAR",
}


@pytest.mark.parametrize(["type", "key"], GOOD_ID_EXAMPLES.items())
def test_validate_key_pass(key, type):
    assert validate_key(key_value=key, key_type=ProductTeamKeyType(type)) == key


@pytest.mark.parametrize(["type", "key"], BAD_ID_EXAMPLES.items())
def test_validate_type_fail_other(key, type):
    with pytest.raises(ValueError):
        validate_key(key_value=key, key_type=ProductTeamKeyType(type))
