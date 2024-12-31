from collections.abc import Generator

from domain.core.device import Device
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my_table"


def repository_fixture[
    T: DeviceRepository | DeviceReferenceDataRepository
](is_integration_test: bool, repository_class: type[T]) -> Generator[T, None, None]:
    if is_integration_test:
        table_name = read_terraform_output("dynamodb_table_name.value")
        client = dynamodb_client()
        yield repository_class(table_name=table_name, dynamodb_client=client)
    else:
        with mock_table(TABLE_NAME) as client:
            yield repository_class(table_name=TABLE_NAME, dynamodb_client=client)


def devices_exactly_equal(device_a: Device, device_b: Device) -> bool:
    public_fields_equal = device_a == device_b
    keys_equal = device_a.keys == device_b.keys
    responses_equal = (
        device_a.questionnaire_responses == device_b.questionnaire_responses
    )
    return public_fields_equal and keys_equal and responses_equal
