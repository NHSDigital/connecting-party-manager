import pytest
from domain.core.cpm_system_id.v1 import CpmSystemIdType
from domain.repository.cpm_system_id_repository import CpmSystemIdRepository
from domain.repository.keys.v3 import TableKey
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


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

    assert current_id is not None
    assert int(current_id["latest"]) == int(start)

    # Simulate an increment in the value (mimic what the generator does)
    new_latest_value = int(start) + 1

    # Update the latest value
    repository.create_or_update(
        key_name=CpmSystemIdType.PARTYKEYNUMBER, new_number=new_latest_value
    )

    updated_id = repository.read(key_name=CpmSystemIdType.PARTYKEYNUMBER)
    assert int(updated_id["latest"]) == expected


@pytest.mark.parametrize(
    "start, expected",
    [
        ("200000099999", 200000100000),
        ("200000109999", 200000110000),
        ("200000119999", 200000120000),
    ],
)
@pytest.mark.integration
def test_asid_generation(start, expected):
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

    assert current_id is not None
    assert int(current_id["latest"]) == int(start)

    # Simulate an increment in the value (mimic what the generator does)
    new_latest_value = int(start) + 1

    # Update the latest value
    repository.create_or_update(
        key_name=CpmSystemIdType.ASIDNUMBER, new_number=new_latest_value
    )

    updated_id = repository.read(key_name=CpmSystemIdType.ASIDNUMBER)
    assert int(updated_id["latest"]) == expected
