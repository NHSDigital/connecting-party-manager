from uuid import UUID

import pytest
from domain.core.device import DeviceKeyType, DeviceStatus, DeviceType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.errors import ItemNotFound

from test_helpers.dynamodb import dynamodb_client, mock_table
from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test__device_repository():
    subject_id = "XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("6f8c285e-04a2-4194-a84e-dabeba474ff7"), name="Team"
    )
    subject = team.create_device(
        id=subject_id,
        name="Subject",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)

    device_repo = DeviceRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    device_repo.write(subject)
    result = device_repo.read(subject_id)
    assert result == subject


@pytest.mark.integration
def test__device_repository__device_does_not_exist():
    subject_id = "XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")

    device_repo = DeviceRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    with pytest.raises(ItemNotFound):
        device_repo.read(subject_id)


def test__device_repository_local():
    subject_id = "XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("6f8c285e-04a2-4194-a84e-dabeba474ff7"), name="Team"
    )
    subject = team.create_device(
        id=subject_id,
        name="Subject",
        type=DeviceType.PRODUCT,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)

    with mock_table(table_name) as client:
        device_repo = DeviceRepository(
            table_name=table_name,
            dynamodb_client=client,
        )

        device_repo.write(subject)
        result = device_repo.read(subject_id)
    assert result == subject


def test__device_repository__device_does_not_exist_local():
    subject_id = "XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")

    with mock_table(table_name) as client:
        device_repo = DeviceRepository(
            table_name=table_name,
            dynamodb_client=client,
        )

        with pytest.raises(ItemNotFound):
            device_repo.read(subject_id)
