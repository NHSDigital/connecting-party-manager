import pytest
from domain.core.cpm_system_id import AsidId, PartyKeyId
from domain.repository.cpm_system_id_repository import CpmSystemIdRepository
from event.aws.client import dynamodb_client

from src.layers.domain.core.cpm_system_id.v1 import CpmSystemIdType, ProductId
from src.layers.domain.repository.keys.v3 import TableKey
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
    current_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
    generator = PartyKeyId.create(current_id=current_id, ods_code="ABC")
    assert generator.latest == 850000
    assert generator.latest_id == "ABC-850000"
    repository.create_or_update(
        key_name=CpmSystemIdType.PARTYKEYNUMBER, new_number=generator.latest
    )
    new_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
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
            "pk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.PARTYKEYNUMBER}"},
            "sk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.PARTYKEYNUMBER}"},
            "latest": {"N": f"{start}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
    generator = PartyKeyId.create(current_id=current_id, ods_code="ABC")
    assert generator.latest == expected
    assert generator.latest_id == f"ABC-{str(expected)}"
    repository.create_or_update(
        key_name=CpmSystemIdType.PARTYKEYNUMBER, new_number=generator.latest
    )
    new_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
    assert new_id["latest"] == expected


@pytest.mark.integration
def test_party_key_generation_increment():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    start_value = 100000

    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": f"CSI#{CpmSystemIdType.PARTYKEYNUMBER}"},
            "sk": {"S": f"CSI#{CpmSystemIdType.PARTYKEYNUMBER}"},
            "latest": {"N": f"{start_value}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)

    # Number of times to call the generator
    num_calls = 5
    current_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)

    previous_latest = int(current_id["latest"])

    for _ in range(num_calls):
        generator = PartyKeyId.create(current_id=current_id, ods_code="ABC")

        expected_latest = previous_latest + 1

        assert generator.latest == expected_latest
        assert generator.latest_id == f"ABC-{expected_latest}"

        # Update repository with new number
        repository.create_or_update(
            key_name=CpmSystemIdType.PARTYKEYNUMBER, new_number=generator.latest
        )

        # Fetch the updated ID and check if it was correctly incremented
        new_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
        assert int(new_id["latest"]) == expected_latest

        # Update for next iteration
        previous_latest = expected_latest
        current_id = new_id

    # Final assertion to check if latest is num_calls greater than start
    final_latest = int(
        repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)["latest"]
    )
    assert final_latest == start_value + num_calls


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
    current_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
    generator = AsidId.create(current_id=current_id)
    assert generator.latest == 200000100000
    assert generator.latest_id == "200000100000"
    repository.create_or_update(
        key_name=CpmSystemIdType.ASIDNUMBER, new_number=generator.latest
    )
    new_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
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
            "pk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.ASIDNUMBER}"},
            "sk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.ASIDNUMBER}"},
            "latest": {"N": f"{start}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)
    current_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
    generator = AsidId.create(current_id=current_id)
    assert generator.latest == expected
    assert generator.latest_id == str(expected)
    repository.create_or_update(
        key_name=CpmSystemIdType.ASIDNUMBER, new_number=generator.latest
    )
    new_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
    assert new_id["latest"] == expected


@pytest.mark.integration
def test_asid_generation_increment():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    start_value = 200000000000

    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.ASIDNUMBER}"},
            "sk": {"S": f"{TableKey.CPM_SYSTEM_ID}#{CpmSystemIdType.ASIDNUMBER}"},
            "latest": {"N": f"{start_value}"},  # Set the initial value for the test
        },
    )

    repository = CpmSystemIdRepository(table_name=TABLE_NAME, dynamodb_client=client)

    # Number of times to call the generator
    num_calls = 5
    current_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)

    previous_latest = int(current_id["latest"])

    for _ in range(num_calls):
        generator = AsidId.create(current_id=current_id)

        expected_latest = previous_latest + 1

        assert generator.latest == expected_latest
        assert generator.latest_id == str(expected_latest)

        # Update repository with new number
        repository.create_or_update(
            key_name=CpmSystemIdType.ASIDNUMBER, new_number=generator.latest
        )

        # Fetch the updated ID and check if it was correctly incremented
        new_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
        assert int(new_id["latest"]) == expected_latest

        # Update for next iteration
        previous_latest = expected_latest
        current_id = new_id

    # Final assertion to check if latest is num_calls greater than start_value
    final_latest = int(repository.read(key_name=CpmSystemIdType.ASIDNUMBER)["latest"])
    assert final_latest == start_value + num_calls


def test_product_id_generator_format_key():
    generator = ProductId.create()
    assert generator.latest_id is not None


@pytest.mark.parametrize(
    "valid_key",
    [
        "P.AAA-333",
        "P.AC3-333",
        "P.ACC-33A",
    ],
)
def test_product_id_generator_validate_key_valid(valid_key):
    is_valid = ProductId.validate_key(key=valid_key)
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
    is_valid = ProductId.validate_key(key=invalid_key)
    assert not is_valid
