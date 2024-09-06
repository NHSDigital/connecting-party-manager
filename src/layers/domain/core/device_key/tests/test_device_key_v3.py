import pytest
from domain.core.device_key.v3 import KeyGenerator, PartyKeyGenerator
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


def test_key_generator_instantiation():
    # Instantiating KeyGenerator directly should raise TypeError
    with pytest.raises(TypeError):
        KeyGenerator(last_used_number=100)


# Mock the database interaction in the KeyGenerator class for testing
class MockKeyGenerator(PartyKeyGenerator):
    def __init__(self, ods_code: str):
        super().__init__(ods_code)

    def get_current_number(self) -> int:
        # Override to return the mock initial number for testing purposes
        return 123

    def update_current_number_in_db(self):
        # Override db call for testing purposes
        pass


def test_party_key_generator_format_key():
    generator = MockKeyGenerator(ods_code="ABC")
    expected_key = "ABC-000124"  # Expecting the number to be formatted with 6 digits
    generated_key = generator.generate_key()
    assert generated_key == expected_key


def test_party_key_generator_validate_key_valid():
    generator = MockKeyGenerator(ods_code="ABC")
    valid_key = "ABC-000124"
    is_valid = generator.validate_key(valid_key)
    assert is_valid


@pytest.mark.parametrize(
    "invalid_key",
    [
        "ABC000124",  # Missing hyphen
        "123-000124",  # Numeric ODS code
        "ABC-1234",  # Number part too short
        "ABC-1234567",  # Number part too long
        "AB1-000124",  # ODS code contains a digit
        "ABC-0001A4",  # Number part contains a non-digit character
        "",  # Empty string
    ],
)
def test_party_key_generator_validate_key_invalid_format(invalid_key):
    generator = MockKeyGenerator(ods_code="ABC")
    is_valid = generator.validate_key(invalid_key)
    assert not is_valid


def test_party_key_generator_increment_number():
    # Test that the number is incremented correctly
    generator = MockKeyGenerator(ods_code="XYZ")
    expected_key = "XYZ-000124"  # Expecting increment from 123456 to 123457
    generated_key = generator.generate_key()
    assert generated_key == expected_key


TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
DUMMY_PARTYKEYNUMBER = 123456


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

    expected_key = "ABC-123457"  # The next number after 123457
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
    assert updated_latest_value == 123457
