from uuid import UUID

import boto3
import pytest
from domain.core.device import DeviceKeyType, DeviceStatus, DeviceType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository

from test_helpers.terraform import read_terraform_output


@pytest.mark.wip
@pytest.mark.integration
def test__device_repository():
    subject_id = UUID("774c8c06-0d15-4b7d-9c7e-4a358681b78b")
    target_id = UUID("07bca737-1022-494c-8df0-5e7dd152ba59")
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(
        id=UUID("6f8c285e-04a2-4194-a84e-dabeba474ff7"), name="Team"
    )
    subject = team.create_device(
        id=subject_id,
        name="Subject",
        type=DeviceType.SERVICE,
        status=DeviceStatus.ACTIVE,
    )
    subject.add_key(key="WWW-XXX", type=DeviceKeyType.PRODUCT_ID)
    subject.add_key(key="1234567890", type=DeviceKeyType.ACCREDITED_SYSTEM_ID)

    device_repo = DeviceRepository(
        table_name=table_name, dynamodb_client=boto3.client("dynamodb")
    )

    device_repo.write(subject)
    result = device_repo.read(subject_id)
    assert result == subject