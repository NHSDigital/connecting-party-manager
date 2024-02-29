from uuid import UUID, uuid4

import pytest
from domain.core.device import DeviceKeyType, DeviceStatus, DeviceType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from domain.repository.marshall import unmarshall
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import clear_dynamodb_table, mock_table
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my_table"


@pytest.mark.integration
def test__device_repository():
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("6f8c285e-04a2-4194-a84e-dabeba474ff7"), name="Team"
    )
    subject = team.create_device(
        name="Subject",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="P.WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="ABC:1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    device_repo = DeviceRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    device_repo.write(subject)
    result = device_repo.read(subject.id)
    assert result == subject


@pytest.mark.integration
def test__device_repository_already_exists():
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7",
        name="Team",
    )
    subject = team.create_device(
        name="Subject",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="P.WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="ABC:1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)

    client = dynamodb_client()
    clear_dynamodb_table(client=client, table_name=table_name)
    device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
    device_repo.write(subject)

    with pytest.raises(AlreadyExistsError):
        device_repo.write(subject)


@pytest.mark.integration
def test__device_repository__device_does_not_exist():
    subject_id = "6f8c285e-04a2-4194-a84e-dabeba474ff7"
    table_name = read_terraform_output("dynamodb_table_name.value")

    client = dynamodb_client()
    clear_dynamodb_table(client=client, table_name=table_name)
    device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)

    with pytest.raises(ItemNotFound):
        device_repo.read(subject_id)


def test__device_repository_local():
    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7",
        name="Team",
    )
    subject = team.create_device(
        name="Subject",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="P.WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="ABC:1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    with mock_table(TABLE_NAME) as client:
        device_repo = DeviceRepository(
            table_name=TABLE_NAME,
            dynamodb_client=client,
        )

        device_repo.write(subject)
        result = device_repo.read(subject.id)
    assert result == subject


def test__device_repository__device_does_not_exist_local():
    subject_id = "6f8c285e-04a2-4194-a84e-dabeba474ff7"

    with mock_table(TABLE_NAME) as client:
        device_repo = DeviceRepository(
            table_name=TABLE_NAME,
            dynamodb_client=client,
        )

        with pytest.raises(ItemNotFound):
            device_repo.read(subject_id)


@pytest.mark.integration
def test__device_repository__query_by_key_type():
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    clear_dynamodb_table(client=client, table_name=table_name)

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=uuid4(), name="Team")
    device_3 = team.create_device(name="Device_3", type=DeviceType.PRODUCT)
    device_3.add_key(key="DEF:3333333333", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    device_4 = team.create_device(name="Device_4", type=DeviceType.ENDPOINT)
    device_4.add_key(
        key="DEF-444:4444444444", type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )

    device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
    device_repo.write(device_3)
    device_repo.write(device_4)

    result = device_repo.query_by_key_type(
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_4.id)

    result = device_repo.query_by_key_type(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_3.id)


@pytest.mark.integration
def test__device_repository__query_by_type():
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    clear_dynamodb_table(client=client, table_name=table_name)

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=uuid4(), name="Team")
    device_3 = team.create_device(name="Device_3", type=DeviceType.PRODUCT)
    device_3.add_key(key="DEF:3333333333", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    device_4 = team.create_device(name="Device_4", type=DeviceType.ENDPOINT)
    device_4.add_key(
        key="DEF-444:4444444444", type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID
    )

    device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
    device_repo.write(device_3)
    device_repo.write(device_4)

    result = device_repo.query_by_device_type(type=DeviceType.ENDPOINT)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_4.id)

    result = device_repo.query_by_device_type(type=DeviceType.PRODUCT)
    (_device,) = map(unmarshall, result["Items"])
    assert _device["id"] == str(device_3.id)
