from copy import deepcopy
from typing import Generator

import pytest
from domain.core.device.v2 import Device, DeviceTag
from domain.repository.device_repository.v2 import DeviceRepository
from domain.repository.keys.v2 import TableKey
from domain.repository.marshall import unmarshall
from etl_utils.io import pkl_load_lz4
from event.aws.client import dynamodb_client as get_dynamodb_client
from mypy_boto3_s3 import S3Client

from etl.sds.worker.load.tests.test_load_worker import MockDeviceRepository
from test_helpers.terraform import read_terraform_output

from .conftest import ETL_BUCKET, parametrize_over_scenarios
from .utils import Handler, Scenario, convert_list_likes, device_as_json_dict


def get_first_key(device: dict[str, list[dict[str, str]]]):
    return tuple(device["keys"][0].values())


def sort_tags(tags: list[dict[str, list[list[str]]]]):
    if tags and isinstance(tags[0], dict):
        _tags = [
            DeviceTag(**{k: v for k, v in tag["components"]}).value for tag in tags
        ]
    else:
        _tags = [DeviceTag(__root__=tag).value for tag in tags]
    return sorted(_tags)


def sort_devices(devices: list[dict]):
    devices_without_dates = []
    for device in devices:
        _device = deepcopy(device)
        _device.pop("created_on", None)
        _device.pop("deleted_on", None)
        _device.pop("updated_on", None)
        _device["tags"] = sort_tags(tags=_device["tags"])
        devices_without_dates.append(_device)

    sorted_devices = sorted(
        devices_without_dates,
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
        for response in questionnaire_response["answers"]
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
        devices = list(TableKey.DEVICE.filter(items, key="sk"))
        for device in devices:
            if device.get("root"):
                yield self.read(device["id"])


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
        transform_response = transform_handler(
            event={"max_records": 1, "etl_type": "updates"}, context=None
        )
        error_message = transform_response.get("error_message")
        if error_message:
            raise EtlError(error_message)
        unprocessed_transform_records = transform_response.get("unprocessed_records")

        unprocessed_load_records = None
        while unprocessed_load_records is None or unprocessed_load_records > 0:
            load_response = load_handler(
                event={"max_records": 1, "etl_type": "updates"}, context=None
            )
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
        if not scenario.expected_errors:
            raise
        (expected_error_snippet,) = scenario.expected_errors
        try:
            assert expected_error_snippet in str(error)
        except AssertionError:
            print("Snippet not found in error message, see below diff:")  # noqa: T201
            assert str(error) == expected_error_snippet
        return

    n_expected_errors = len(scenario.expected_errors)
    assert (
        n_expected_errors == 0
    ), f"{n_expected_errors} errors were expected but none were raised"

    dynamodb_client = get_dynamodb_client()
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = MockDeviceRepository(table_name=table_name, dynamodb_client=dynamodb_client)
    devices = list(map(device_as_json_dict, repo.all_devices()))
    assert len(devices) == len(scenario.load_output), devices
    assert sort_devices(devices) == sort_devices(scenario.load_output), devices
