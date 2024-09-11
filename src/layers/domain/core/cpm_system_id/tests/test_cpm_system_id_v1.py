import pytest
from domain.core.cpm_system_id import AsidId, PartyKeyId
from domain.repository.cpm_system_id_repository import CpmSystemIdRepository
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


def test_party_key_generator_format_key():
    generator = PartyKeyId.create(current_id={"latest": 123456}, ods_code="ABC")
    expected_key = "ABC-123457"  # Expecting the number to be formatted with 6 digits
    assert generator.latest_id == expected_key


def test_party_key_generator_validate_key_valid():
    valid_key = "ABC-123457"
    is_valid = PartyKeyId.validate_key(valid_key)
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
    is_valid = PartyKeyId.validate_key(invalid_key)
    assert not is_valid


def test_party_key_generator_increment_number():
    # Test that the number is incremented correctly
    generator = PartyKeyId.create(current_id={"latest": 123456}, ods_code="XYZ")
    expected_key = "XYZ-123457"  # Expecting increment from 123456 to 123457
    assert generator.latest == 123457
    assert generator.latest_id == expected_key


@pytest.mark.integration
def test_party_key_generation_seeded():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name="PARTYKEYNUMBER")
    generator = PartyKeyId.create(current_id=current_id, ods_code="ABC")
    assert generator.latest == 850000
    assert generator.latest_id == "ABC-850000"
    repository.create_or_update(key_name="PARTYKEYNUMBER", new_number=generator.latest)
    new_id = repository.read(key_name="PARTYKEYNUMBER")
    assert new_id["latest"] == 850000


@pytest.mark.parametrize(
    "start, expected",
    [("850010", 850011), ("875789", 875790), ("961237", 961238)],
)
@pytest.mark.integration
def test_party_key_generation(start, expected):
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": "CSI#PARTYKEYNUMBER"},
            "sk": {"S": "CSI#PARTYKEYNUMBER"},
            "latest": {"N": f"{start}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name="PARTYKEYNUMBER")
    generator = PartyKeyId.create(current_id=current_id, ods_code="ABC")
    assert generator.latest == expected
    assert generator.latest_id == f"ABC-{str(expected)}"
    repository.create_or_update(key_name="PARTYKEYNUMBER", new_number=generator.latest)
    new_id = repository.read(key_name="PARTYKEYNUMBER")
    assert new_id["latest"] == expected


def test_asid_generator_validate_key_valid():
    valid_key = "223456789014"
    is_valid = AsidId.validate_key(valid_key)
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
    is_valid = AsidId.validate_key(invalid_key)
    assert not is_valid


def test_asid_generator_increment_number():
    # Test that the number is incremented correctly
    generator = AsidId.create(current_id={"latest": 223456789012})
    assert generator.latest == 223456789013
    assert generator.latest_id == "223456789013"


@pytest.mark.integration
def test_asid_key_generation_seeded():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name="ASIDNUMBER")
    generator = AsidId.create(current_id=current_id)
    assert generator.latest == 200000100000
    assert generator.latest_id == "200000100000"
    repository.create_or_update(key_name="ASIDNUMBER", new_number=generator.latest)
    new_id = repository.read(key_name="ASIDNUMBER")
    assert new_id["latest"] == 200000100000


@pytest.mark.parametrize(
    "start, expected",
    [
        ("200000000000", 200000000001),
        ("200001000000", 200001000001),
        ("200001000009", 200001000010),
    ],
)
@pytest.mark.integration
def test_asid_key_generation(start, expected):
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": "CSI#ASIDNUMBER"},
            "sk": {"S": "CSI#ASIDNUMBER"},
            "latest": {"N": f"{start}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name="ASIDNUMBER")
    generator = AsidId.create(current_id=current_id)
    assert generator.latest == expected
    assert generator.latest_id == str(expected)
    repository.create_or_update(key_name="ASIDNUMBER", new_number=generator.latest)
    new_id = repository.read(key_name="ASIDNUMBER")
    assert new_id["latest"] == expected
