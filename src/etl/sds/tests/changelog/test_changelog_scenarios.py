from typing import Generator

import pytest
from domain.core.device import Device
from domain.repository.device_repository import DeviceRepository
from domain.repository.keys import TableKeys
from domain.repository.marshall import unmarshall
from etl_utils.io import pkl_load_lz4
from event.aws.client import dynamodb_client as get_dynamodb_client
from mypy_boto3_s3 import S3Client

from etl.sds.worker.load.tests.test_load_worker import MockDeviceRepository

from .conftest import ETL_BUCKET, TABLE_NAME, parametrize_over_scenarios
from .utils import Handler, Scenario, convert_list_likes, device_as_json_dict


def get_first_key(device: dict[str, dict[str, str]]):
    keys = list(device.get("keys", {"": ""}).keys())
    return keys[0]


def sort_devices(devices: list[dict]):
    sorted_devices = sorted(
        devices,
        key=lambda device: (
            device.get("name"),
            device.get("ods_code"),
            get_first_key(device),
        ),
    )
    responses = [
        response
        for device in sorted_devices
        for questionnaire_responses in device.get(
            "questionnaire_responses", {}
        ).values()
        for questionnaire_response in questionnaire_responses
        for response in questionnaire_response["responses"]
    ]
    for response in responses:
        ((field, answers),) = response.items()
        response[field] = sorted(answers)

    return sorted_devices


class EtlError(Exception):
    pass


class MockDeviceRepository(DeviceRepository):
    def all_devices(self) -> Generator[Device, None, None]:
        response = self.client.scan(TableName=self.table_name)
        items = list(map(unmarshall, response["Items"]))
        devices = list(TableKeys.DEVICE.filter(items, key="sk"))
        for device in devices:
            yield self.read(id=device["id"])


@parametrize_over_scenarios()
def test_extract(scenario: Scenario, extract_handler: Handler, s3_client: S3Client):
    handler_response = extract_handler(event={}, context=None)
    error_message = handler_response.get("error_message")
    assert not error_message, error_message

    response = s3_client.get_object(
        Bucket=ETL_BUCKET, Key="input--transform/unprocessed"
    )
    actual_extract_output = pkl_load_lz4(response["Body"])
    assert convert_list_likes(actual_extract_output) == convert_list_likes(
        scenario.extract_output
    )


def run_transform_and_load(transform_handler: Handler, load_handler: Handler):
    unprocessed_transform_records = None
    while unprocessed_transform_records is None or unprocessed_transform_records > 0:
        transform_response = transform_handler(event={"max_records": 1}, context=None)
        error_message = transform_response.get("error_message")
        if error_message:
            raise EtlError(error_message)
        unprocessed_transform_records = transform_response.get("unprocessed_records")

        unprocessed_load_records = None
        while unprocessed_load_records is None or unprocessed_load_records > 0:
            load_response = load_handler(event={"max_records": 1}, context=None)
            error_message = load_response.get("error_message")
            if error_message:
                raise EtlError(error_message)
            unprocessed_load_records = load_response.get("unprocessed_records")


@pytest.mark.integration
@parametrize_over_scenarios()
def test_transform_and_load(
    scenario: Scenario, transform_handler: Handler, load_handler: Handler
):
    try:
        run_transform_and_load(
            transform_handler=transform_handler, load_handler=load_handler
        )
    except EtlError as error:
        assert any(_error in str(error) for _error in scenario.expected_errors), str(
            error
        )
        return

    n_expected_errors = len(scenario.expected_errors)
    assert (
        n_expected_errors == 0
    ), f"{n_expected_errors} errors were expected but none were raised"

    dynamodb_client = get_dynamodb_client()
    repo = MockDeviceRepository(table_name=TABLE_NAME, dynamodb_client=dynamodb_client)
    devices = list(map(device_as_json_dict, repo.all_devices()))
    assert len(devices) == len(scenario.load_output), devices

    assert sort_devices(devices) == sort_devices(scenario.load_output), devices
