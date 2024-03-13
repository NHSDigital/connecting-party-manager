from typing import Generator

import pytest
from domain.core.device import Device
from domain.repository.device_repository import DeviceRepository
from event.aws.client import dynamodb_client
from pytest import FixtureRequest

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my_table"


@pytest.fixture
def repository(request: FixtureRequest) -> Generator[DeviceRepository, None, None]:
    if request.node.get_closest_marker("integration"):
        table_name = read_terraform_output("dynamodb_table_name.value")
        client = dynamodb_client()
        yield DeviceRepository(table_name=table_name, dynamodb_client=client)
    else:
        with mock_table(TABLE_NAME) as client:
            yield DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)


def devices_exactly_equal(device_a: Device, device_b: Device) -> bool:
    public_fields_equal = device_a == device_b
    keys_equal = device_a.keys == device_b.keys
    responses_equal = (
        device_a.questionnaire_responses == device_b.questionnaire_responses
    )
    return public_fields_equal and keys_equal and responses_equal
