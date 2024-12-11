from unittest import mock

import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import QuestionnaireResponse
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.epr.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.tests.test_creators import as_device
from sds.epr.updates.change_request_routing import process_change_request
from sds.epr.updates.etl_device_repository import EtlDeviceRepository

from test_helpers.dynamodb import mock_table


@pytest.fixture
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture
def product(product_team):
    return create_epr_product(
        product_team=product_team, product_name="foo", party_key="AAA-111111"
    )


@pytest.fixture
def additional_interactions(product: CpmProduct):
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=[],
    )


@pytest.fixture
def message_sets(product: CpmProduct):
    return create_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        message_set_data=[],
    )


@pytest.fixture
def mhs_device_data():
    questionnaire = QuestionnaireRepository().read(name=QuestionnaireInstance.SPINE_MHS)
    raw_mhs_device_data = {
        "Address": "my-mhs-endpoint",
        "Approver URP": "approver-123",
        "Contract Property Template Key": "key-123",
        "DNS Approver": "dns-approver-123",
        "Date Approved": "today",
        "Date DNS Approved": "yesterday",
        "Date Requested": "a week ago",
        "Interaction Type": "hl7",
        "MHS CPA ID": "1wd354",
        "MHS FQDN": "my-fqdn",
        "MHS Is Authenticated": "none",
        "MHS Party key": "AAA-123456",
        "Managing Organization": "AAA",
        "Product Key": "key-123",
        "Product Name": "My EPR Product",
        "Requestor URP": "requester-123",
        "Unique Identifier": "1wd354",
        "MHS Manufacturer Organisation": "AAA",
    }
    return questionnaire.validate(data=raw_mhs_device_data)


@pytest.fixture
def mhs_device(
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    mhs_device_data: QuestionnaireResponse,
):
    return create_mhs_device(
        cpa_ids=["er3243"],
        party_key=product.keys[0].key_value,
        product=product,
        message_sets_id=message_sets.id,
        mhs_device_data=mhs_device_data,
    )


def mock_patch(module: str):
    return mock.patch(
        f"sds.epr.updates.change_request_routing.{module}",
        return_value=f"called '{module}'",
    )


@pytest.fixture
def as_device(
    product,
    message_sets: DeviceReferenceData,
    additional_interactions: DeviceReferenceData,
):
    questionnaire = QuestionnaireRepository().read(name=QuestionnaireInstance.SPINE_AS)
    as_device_data = questionnaire.validate(
        {
            "ASID": "123456",
            "MHS Manufacturer Organisation": "AAA",
            "Approver URP": "approver-123",
            "Client ODS Codes": ["ABC", "CDE", "EFG"],
            "Date Approved": "today",
            "Date Requested": "a week ago",
            "ODS Code": "AAA",
            "Party Key": "AAA-123456",
            "Product Key": "key-123",
            "Requestor URP": "requester-123",
        }
    )
    return create_as_device(
        product=product,
        party_key="AAA-123456",
        asid="123456",
        as_device_data=as_device_data,
        message_sets_id=str(message_sets.id),
        additional_interactions_id=str(additional_interactions.id),
        as_tags=[
            {
                "nhs_as_client": "CDE",
                "nhs_as_svc_ia": "interaction-id-1",
                "nhs_mhs_manufacturer_org": "AAA",
                "nhs_mhs_party_key": "AAA-123456",
            },
            {
                "nhs_as_client": "ABC",
                "nhs_as_svc_ia": "interaction-id-1",
                "nhs_mhs_party_key": "AAA-123456",
            },
        ],
    )


DEFAULT_KWARGS = dict(
    product_team_repository=None,
    product_repository=None,
    device_repository=None,
    device_reference_data_repository=None,
    mhs_device_questionnaire=None,
    mhs_device_field_mapping=None,
    accredited_system_questionnaire=None,
    accredited_system_field_mapping=None,
    message_set_questionnaire=None,
    message_set_field_mapping=None,
    additional_interactions_questionnaire=None,
)


def test_process_change_request_add_mhs():
    with mock_patch("process_request_to_add_mhs"):
        assert (
            process_change_request(
                record={"unique_identifier": "123", "object_class": "nhsmhs"},
                etl_device_repository=None,
                **DEFAULT_KWARGS,
            )
            == "called 'process_request_to_add_mhs'"
        )


def test_process_change_request_add_as():
    with mock_patch("process_request_to_add_as"):
        assert (
            process_change_request(
                record={"unique_identifier": "123", "object_class": "nhsas"},
                etl_device_repository=None,
                **DEFAULT_KWARGS,
            )
            == "called 'process_request_to_add_as'"
        )


def test_process_change_request_not_found():
    table_name = "my-table"
    with mock_table(table_name) as client:
        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)

        assert (
            process_change_request(
                record={"unique_identifier": "123", "object_class": "other"},
                etl_device_repository=etl_repo,
                **DEFAULT_KWARGS,
            )
            == []
        )


def test_process_change_request_delete_mhs(mhs_device):
    cpa_id = "12345"
    mhs_device.add_key(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id)

    table_name = "my-table"
    with mock_patch("process_request_to_delete_mhs"), mock_table(table_name) as client:
        standard_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        standard_repo.write(mhs_device)

        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        assert (
            process_change_request(
                record={"unique_identifier": cpa_id, "object_class": "delete"},
                etl_device_repository=etl_repo,
                **DEFAULT_KWARGS,
            )
            == "called 'process_request_to_delete_mhs'"
        )


def test_process_change_request_delete_as(as_device):
    table_name = "my-table"
    with mock_patch("process_request_to_delete_as"), mock_table(table_name) as client:
        standard_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        standard_repo.write(as_device)

        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        assert (
            process_change_request(
                record={"unique_identifier": "123456", "object_class": "delete"},
                etl_device_repository=etl_repo,
                **DEFAULT_KWARGS,
            )
            == "called 'process_request_to_delete_as'"
        )


def test_process_change_request_modify_mhs(mhs_device: Device):
    cpa_id = "12345"
    mhs_device.add_key(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id)

    table_name = "my-table"
    with mock_patch("route_mhs_modification_request"), mock_table(table_name) as client:
        standard_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        standard_repo.write(mhs_device)

        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        assert (
            process_change_request(
                record={"unique_identifier": cpa_id, "object_class": "modify"},
                etl_device_repository=etl_repo,
                **DEFAULT_KWARGS,
            )
            == "called 'route_mhs_modification_request'"
        )


def test_process_change_request_modify_as(as_device):
    table_name = "my-table"
    with mock_patch("route_as_modification_request"), mock_table(table_name) as client:
        standard_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        standard_repo.write(as_device)

        etl_repo = EtlDeviceRepository(table_name=table_name, dynamodb_client=client)
        assert (
            process_change_request(
                record={"unique_identifier": "123456", "object_class": "modify"},
                etl_device_repository=etl_repo,
                **DEFAULT_KWARGS,
            )
            == "called 'route_as_modification_request'"
        )
