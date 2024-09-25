import pytest
from domain.core.cpm_system_id.v1 import AsidId, CpmSystemIdType, PartyKeyId
from domain.repository.cpm_system_id_repository import CpmSystemIdRepository
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall_value
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


@pytest.mark.parametrize(
    "start, expected",
    [("850010", 850011), ("875789", 875790), ("961237", 961238)],
)
@pytest.mark.integration
def test_party_key_generation(start, expected):
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=table_name,
        Item={
            "pk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.PARTY_KEY_NUMBER)},
            "sk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.PARTY_KEY_NUMBER)},
            "latest_number": marshall_value(start),  # Set initial value for the test
        },
    )

    repository = CpmSystemIdRepository[PartyKeyId](
        table_name=table_name, dynamodb_client=client, model=PartyKeyId
    )
    party_key = repository.read(key_name=CpmSystemIdType.PARTY_KEY_NUMBER)
    new_party_key = PartyKeyId.create(
        current_number=party_key.latest_number, ods_code="ABC"
    )
    assert new_party_key.latest_number == expected
    assert new_party_key.id == f"ABC-{str(expected)}"
    repository.create_or_update(
        key_name=CpmSystemIdType.PARTY_KEY_NUMBER,
        new_number=new_party_key.latest_number,
    )
    updated_new_party_key = repository.read(key_name=CpmSystemIdType.PARTY_KEY_NUMBER)
    assert updated_new_party_key.latest_number == expected


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
            "pk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.ASID_NUMBER)},
            "sk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.ASID_NUMBER)},
            "latest_number": marshall_value(start),  # Set initial value for the test
        },
    )

    repository = CpmSystemIdRepository[AsidId](
        table_name=TABLE_NAME, dynamodb_client=client, model=AsidId
    )
    asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)
    new_asid = AsidId.create(current_number=asid.latest_number)
    assert new_asid.latest_number == expected
    assert new_asid.id == str(expected)
    repository.create_or_update(
        key_name=CpmSystemIdType.ASID_NUMBER, new_number=new_asid.latest_number
    )
    updated_new_asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)
    assert updated_new_asid.latest_number == expected


@pytest.mark.integration
def test_asid_key_generation_seeded():
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    repository = CpmSystemIdRepository[AsidId](
        table_name=table_name, dynamodb_client=client, model=AsidId
    )
    asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)
    new_asid = AsidId.create(current_number=asid.latest_number)
    assert new_asid.latest_number == 200000100000
    assert new_asid.id == "200000100000"
    repository.create_or_update(
        key_name=CpmSystemIdType.ASID_NUMBER, new_number=new_asid.latest_number
    )
    updated_new_asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)
    assert updated_new_asid.latest_number == 200000100000


@pytest.mark.integration
def test_asid_generation_increment():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    start_value = 200000000000

    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.ASID_NUMBER)},
            "sk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.ASID_NUMBER)},
            "latest_number": marshall_value(start_value),  # Set initial value
        },
    )

    repository = CpmSystemIdRepository[AsidId](
        table_name=TABLE_NAME, dynamodb_client=client, model=AsidId
    )

    # Number of times to call the generator
    num_calls = 5
    asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)

    for _ in range(num_calls):
        new_asid = AsidId.create(current_number=asid.latest_number)

        expected_latest = asid.latest_number + 1

        assert new_asid.latest_number == expected_latest
        assert new_asid.id == str(expected_latest)

        # Update repository with new number
        repository.create_or_update(
            key_name=CpmSystemIdType.ASID_NUMBER, new_number=new_asid.latest_number
        )

        # Fetch the updated ID and check if it was correctly incremented
        updated_new_asid = repository.read(key_name=CpmSystemIdType.ASID_NUMBER)
        assert updated_new_asid.latest_number == expected_latest

        # Update for next iteration
        asid = updated_new_asid

    # Final assertion to check if latest is num_calls greater than start_value
    final_latest = repository.read(key_name=CpmSystemIdType.ASID_NUMBER).latest_number
    assert final_latest == start_value + num_calls


@pytest.mark.integration
def test_party_key_generation_seeded():
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    repository = CpmSystemIdRepository[PartyKeyId](
        table_name=table_name, dynamodb_client=client, model=PartyKeyId
    )
    current_party_key = repository.read(key_name=CpmSystemIdType.PARTY_KEY_NUMBER)
    new_party_key = PartyKeyId.create(
        current_number=current_party_key.latest_number, ods_code="ABC"
    )
    assert new_party_key.latest_number == 850000
    assert new_party_key.id == "ABC-850000"
    repository.create_or_update(
        key_name=CpmSystemIdType.PARTY_KEY_NUMBER,
        new_number=new_party_key.latest_number,
    )
    updated_new_party_key = repository.read(key_name=CpmSystemIdType.PARTY_KEY_NUMBER)
    assert updated_new_party_key.latest_number == 850000


@pytest.mark.integration
def test_party_key_generation_increment():
    TABLE_NAME = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    start_value = 100000

    # Insert a dummy entry with an initial 'latest' value
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            "pk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.PARTY_KEY_NUMBER)},
            "sk": {"S": TableKey.CPM_SYSTEM_ID.key(CpmSystemIdType.PARTY_KEY_NUMBER)},
            "latest_number": marshall_value(start_value),  # Set initial value
        },
    )
    repository = CpmSystemIdRepository[PartyKeyId](
        table_name=TABLE_NAME, dynamodb_client=client, model=PartyKeyId
    )

    # Number of times to call the generator
    num_calls = 5
    party_key = repository.read(key_name=CpmSystemIdType.PARTY_KEY_NUMBER)

    for _ in range(num_calls):
        new_party_key = PartyKeyId.create(
            current_number=party_key.latest_number, ods_code="ABC"
        )

        expected_latest = party_key.latest_number + 1

        assert new_party_key.latest_number == expected_latest
        assert new_party_key.id == f"ABC-{expected_latest}"

        # Update repository with new number
        repository.create_or_update(
            key_name=CpmSystemIdType.PARTY_KEY_NUMBER,
            new_number=new_party_key.latest_number,
        )

        # Fetch the updated ID and check if it was correctly incremented
        updated_new_party_key = repository.read(
            key_name=CpmSystemIdType.PARTY_KEY_NUMBER
        )
        assert updated_new_party_key.latest_number == expected_latest

        # Update for next iteration
        party_key = new_party_key

    # Final assertion to check if latest is num_calls greater than start
    final_latest = repository.read(
        key_name=CpmSystemIdType.PARTY_KEY_NUMBER
    ).latest_number
    assert final_latest == start_value + num_calls
