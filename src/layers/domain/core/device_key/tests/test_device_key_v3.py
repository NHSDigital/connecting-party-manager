import pytest
from domain.core.device_key.v3 import ASIDGenerator, KeyGenerator, PartyKeyGenerator
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


def test_key_generator_instantiation():
    # Instantiating KeyGenerator directly should raise TypeError
    with pytest.raises(TypeError):
        KeyGenerator(last_used_number=100)


def test_party_key_generator_format_key():
    generator = PartyKeyGenerator(last_used_number=123, ods_code="ABC")
    expected_key = "ABC-0000124"
    generated_key = generator.generate_key()
    assert generated_key == expected_key


def test_party_key_generator_validate_key_valid():
    generator = PartyKeyGenerator(last_used_number=123, ods_code="ABC")
    valid_key = "ABC-0000124"
    is_valid = generator.validate_key(valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "ABC0000124",  # Missing hyphen
        "123-0000124",  # Numeric ODS code
        "ABC-1234",  # Number part too short
        "ABC-12345678",  # Number part too long
        "AB1-0000124",  # ODS code contains a digit
        "ABC-00001A4",  # Number part contains a non-digit character
        "",  # Empty string
    ],
)
def test_party_key_generator_validate_key_invalid_format(invalid_key):
    generator = PartyKeyGenerator(last_used_number=123, ods_code="ABC")
    is_valid = generator.validate_key(invalid_key)
    assert not is_valid


def test_party_key_generator_increment_number():
    # Test that the number is incremented correctly
    generator = PartyKeyGenerator(last_used_number=9999999, ods_code="XYZ")
    expected_key = "XYZ-10000000"  # Check boundary condition for 7-digit number
    generated_key = generator.generate_key()
    assert generated_key == expected_key


def test_asid_generator_format_key():
    generator = ASIDGenerator(last_used_number=123)
    expected_key = "00124"
    generated_key = generator.generate_key()
    assert generated_key == expected_key


@pytest.mark.parametrize(
    "valid_key",
    [
        "00001",
        "12345",
        "99999",
    ],
)
def test_asid_generator_validate_key_valid(valid_key):
    generator = ASIDGenerator(last_used_number=123)
    is_valid = generator.validate_key(valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "1234",  # Too short
        "123456",  # Too long
        "12a45",  # Non-digit characters
        "",  # Empty string
    ],
)
def test_asid_generator_validate_key_invalid_format(invalid_key):
    generator = ASIDGenerator(last_used_number=123)
    is_valid = generator.validate_key(invalid_key)
    assert not is_valid


def test_asid_generator_integration():
    generator = ASIDGenerator(last_used_number=999)

    # Generate the next ASID and validate it
    key = generator.generate_key()
    assert key == "01000"
    assert generator.validate_key(key) is True

    # Ensure the next key is incremented correctly
    key = generator.generate_key()
    assert key == "01001"
    assert generator.validate_key(key) is True


TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
DUMMY_PARTYKEYNUMBER = 1234567


@pytest.mark.integration
def test_party_key_generation():
    client = dynamodb_client()

    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": "PARTYKEYNUMBER"},
            "sk": {"S": "PARTYKEYNUMBER"},
            "latest": {
                "N": f"{DUMMY_PARTYKEYNUMBER}"
            },  # Set the initial value for the test
        },
    )

    # Initialize the PartyKeyGenerator
    generator = PartyKeyGenerator(ods_code="ABC")

    expected_key = "ABC-1234568"  # The next number after 1234567
    generated_key = generator.generate_key()

    assert generated_key == expected_key

    # Retrieve the updated entry from DynamoDB
    response = client.get_item(
        TableName=TABLE_NAME,
        Key={
            "pk": {"S": "PARTYKEYNUMBER"},
            "sk": {"S": "PARTYKEYNUMBER"},
        },
    )

    # Extract the 'latest' value from the response and assert it was updated
    updated_latest_value = int(response["Item"]["latest"]["N"])
    assert updated_latest_value == 1234568
