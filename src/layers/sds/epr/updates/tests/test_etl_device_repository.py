from domain.core.enum import Environment
from domain.core.root.v1 import Root
from domain.repository.device_repository.v1 import DeviceRepository
from sds.epr.updates.etl_device_repository import EtlDeviceRepository

from test_helpers.dynamodb import mock_table


def test_EtlDeviceRepository_read_if_exists():
    ods_org = Root.create_ods_organisation(ods_code="AAA")
    product_team = ods_org.create_product_team(name="my product team")
    product = product_team.create_cpm_product(name="my product")
    device = product.create_device(name="my device", environment=Environment.PROD)

    table_name = "my-table"
    with mock_table(table_name) as client:
        standard_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        standard_repo.write(device)
        device_by_path = standard_repo.read(
            product_team_id=device.product_team_id,
            product_id=str(device.product_id),
            environment=Environment.PROD,
            id=str(device.id),
        )

        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        device_by_global_id = etl_repo.read_if_exists(device.id)

    assert device == device_by_path == device_by_global_id


def test_EtlDeviceRepository_read_if_exists_defaults_to_none():
    table_name = "my-table"
    with mock_table(table_name) as client:
        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        device_by_global_id = etl_repo.read_if_exists("does not exist")

    assert device_by_global_id is None
