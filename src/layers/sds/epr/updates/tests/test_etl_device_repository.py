import pytest
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.enum import Environment

from domain.core.root.v1 import Root
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.errors import ItemNotFound
from sds.epr.updates.etl_device import EtlDevice
from sds.epr.updates.etl_device_repository import EtlDeviceRepository

from test_helpers.dynamodb import mock_table


@pytest.fixture
def device():
    ods_org = Root.create_ods_organisation(ods_code="AAA")
    product_team = ods_org.create_product_team(name="my product team")
    product = product_team.create_cpm_product(name="my product")
    _device = product.create_device(name="my device", environment=Environment.PROD)
    _device.add_key(key_type=DeviceKeyType.CPA_ID, key_value="123456")
    _device.add_tag(foo="bar")
    _device.add_tag(foo="bar", bar="foo")
    return _device


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


def state_with_sorted_tags(device: Device) -> dict:
    device_state = device.state()
    device_state["tags"] = sorted(sorted(tag) for tag in device_state["tags"])
    return device_state


def test_EtlDeviceRepository_handle_DeviceHardDeletedEvent(device: Device):
    device_state = state_with_sorted_tags(device)

    table_name = "my-table"
    with mock_table(table_name) as client:
        device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        device_repo.write(device)

        # Check that the Device has been indexed by id
        device_from_db = device_repo.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            id=device.id,
            environment=Environment.PROD,
        )
        device_state_from_db = state_with_sorted_tags(device_from_db)
        assert device_state_from_db == device_state

        # Check that the Device has been indexed by key
        for key in device.keys:
            device_from_db_by_key = device_repo.read(
                product_team_id=device.product_team_id,
                product_id=device.product_id,
                id=key.key_value,
                environment=Environment.PROD,
            )
            device_state_from_db_by_key = state_with_sorted_tags(device_from_db_by_key)
            assert device_state_from_db_by_key == device_state

        # Check that the Device has been indexed by tag
        for tag in device.tags:
            (device_from_db_by_tag,) = device_repo.query_by_tag(**dict(tag.__root__))

            # query_by_tag does not return the Device.tags, so remove them for comparison
            device_state_without_tags = dict(**device_state)
            device_state_without_tags["tags"] = []
            assert device_from_db_by_tag.state() == device_state_without_tags

        etl_device = EtlDevice(**device.state())
        etl_device.hard_delete()
        etl_device_repo = EtlDeviceRepository(
            table_name=table_name, dynamodb_client=client
        )
        etl_device_repo.write(etl_device)

        # Check that the Device indexed by id has been deleted
        with pytest.raises(ItemNotFound):
            device_repo.read(
                product_team_id=device.product_team_id,
                product_id=device.product_id,
                id=device.id,
                environment=Environment.PROD,
            )

        # Check that the Device indexed by key have been deleted
        for key in device.keys:
            with pytest.raises(ItemNotFound):
                device_repo.read(
                    product_team_id=device.product_team_id,
                    product_id=device.product_id,
                    id=key.key_value,
                    environment=Environment.PROD,
                )

        # Check that the Device indexed by tag have been deleted
        for tag in device.tags:
            devices = device_repo.query_by_tag(**dict(tag.__root__))
            assert devices == []
