from uuid import UUID

import pytest
from domain.core.device import DeviceKeyType, DeviceStatus, DeviceType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output


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
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
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
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)

    device_repo = DeviceRepository(
        table_name=table_name, dynamodb_client=dynamodb_client()
    )
    device_repo.write(subject)

    with pytest.raises(AlreadyExistsError):
        device_repo.write(subject)


@pytest.mark.integration
def test__device_repository__device_does_not_exist():
    subject_id = "6f8c285e-04a2-4194-a84e-dabeba474ff7"
    table_name = read_terraform_output("dynamodb_table_name.value")

    device_repo = DeviceRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

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
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)
    with mock_table("my_table") as client:
        device_repo = DeviceRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        device_repo.write(subject)
        result = device_repo.read(subject.id)
    assert result == subject


def test__device_repository__device_does_not_exist_local():
    subject_id = "6f8c285e-04a2-4194-a84e-dabeba474ff7"

    with mock_table("my_table") as client:
        device_repo = DeviceRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        with pytest.raises(ItemNotFound):
            device_repo.read(subject_id)
