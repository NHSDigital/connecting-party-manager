from unittest import mock

import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.device import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import QuestionnaireResponse
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from event.json import json_loads
from sds.epr.bulk_create.bulk_create import create_complete_epr_product


@pytest.fixture
def ods_code():
    return "AAA"


@pytest.fixture
def party_key():
    return "AAA-123456"


@pytest.fixture
def product_name():
    return "My EPR Product"


@pytest.fixture
def mhs_data():
    return {
        "questionnaire_name": "spine_mhs",
        "questionnaire_version": "1",
        "data": {
            "Unique Identifier": "1wd354",
            "Approver URP": "approver-123",
            "Contract Property Template Key": "key-123",
            "Date Approved": "today",
            "Date DNS Approved": "yesterday",
            "Date Requested": "a week ago",
            "DNS Approver": "dns-approver-123",
            "Interaction Type": "hl7",
            "Managing Organization": "AAA",
            "MHS CPA ID": "1wd354",
            "Address": "my-mhs-endpoint",
            "MHS FQDN": "my-fqdn",
            "MHS Is Authenticated": "none",
            "MHS Party key": "AAA-123456",
            "Product Key": "key-123",
            "Product Name": "My EPR Product",
            "Requestor URP": "requester-123",
            "MHS Manufacturer Organisation": "AAA",
        },
    }


@pytest.fixture
def message_set_data():
    return [
        {
            "questionnaire_name": "spine_mhs_message_sets",
            "questionnaire_version": "1",
            "data": {
                "MHS IN": "in-123",
                "MHS SN": "sn-123",
                "Interaction ID": "my-interaction-id",
            },
        },
        {
            "questionnaire_name": "spine_mhs_message_sets",
            "questionnaire_version": "1",
            "data": {
                "MHS IN": "in-456",
                "MHS SN": "sn-456",
                "Interaction ID": "my-other-interaction-id",
            },
        },
    ]


@pytest.fixture
def mhs_cpa_ids():
    return ["1wd354", "h0394j"]


@pytest.fixture
def mhs_tags():
    return []


@pytest.fixture
def additional_interactions_data():
    return [
        {
            "questionnaire_name": "spine_as_additional_interactions",
            "questionnaire_version": "1",
            "data": {"Interaction ID": "interaction-id-1"},
        },
        {
            "questionnaire_name": "spine_as_additional_interactions",
            "questionnaire_version": "1",
            "data": {"Interaction ID": "interaction-id-2"},
        },
        {
            "questionnaire_name": "spine_as_additional_interactions",
            "questionnaire_version": "1",
            "data": {"Interaction ID": "interaction-id-4"},
        },
    ]


@pytest.fixture
def as_device_data():
    return [
        {
            "questionnaire_name": "spine_as",
            "questionnaire_version": "1",
            "data": {
                "ASID": "123456",
                "Approver URP": "approver-123",
                "Date Approved": "today",
                "Requestor URP": "requester-123",
                "Date Requested": "a week ago",
                "ODS Code": "AAA",
                "MHS Manufacturer Organisation": "AAA",
                "Party Key": "AAA-123456",
                "Product Key": "key-123",
                "Client ODS Codes": ["ABC", "CDE", "EFG"],
            },
        },
        {
            "questionnaire_name": "spine_as",
            "questionnaire_version": "1",
            "data": {
                "ASID": "456789",
                "Approver URP": "approver-456",
                "Date Approved": "today",
                "Requestor URP": "requester-456",
                "Date Requested": "a week ago",
                "ODS Code": "BBB",
                "MHS Manufacturer Organisation": "AAA",
                "Party Key": "AAA-456789",
                "Product Key": "key-123",
                "Client ODS Codes": ["ABC", "JKL", "LMN"],
            },
        },
    ]


@pytest.fixture
def as_tags():
    return [
        [
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "interaction-id-1",
            },
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "interaction-id-1",
                "nhs_mhs_party_key": "AAA-123456",
            },
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "interaction-id-2",
            },
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "interaction-id-2",
                "nhs_mhs_party_key": "AAA-123456",
            },
        ],
        [
            {
                "nhs_id_code": "BBB",
                "nhs_as_svc_ia": "interaction-id-2",
            },
            {
                "nhs_id_code": "BBB",
                "nhs_as_svc_ia": "interaction-id-2",
                "nhs_mhs_party_key": "AAA-456789",
            },
            {
                "nhs_id_code": "BBB",
                "nhs_as_svc_ia": "interaction-id-4",
            },
            {
                "nhs_id_code": "BBB",
                "nhs_as_svc_ia": "interaction-id-4",
                "nhs_mhs_party_key": "AAA-456789",
            },
        ],
    ]


def _fix_up_questionnaire(qr: QuestionnaireResponse, today_string: str) -> dict:
    _qr = json_loads(qr.json())
    assert _qr.pop("created_on").startswith(today_string)
    _qr.pop("id")
    return _qr


def _assert_list_of_dict_equal(a: list[dict], b: list[dict]):
    _a = sorted(map(sorted, map(dict.items, a)))
    _b = sorted(map(sorted, map(dict.items, b)))
    assert _a == _b


@mock.patch(
    "sds.epr.bulk_create.bulk_create._create_complete_epr_product",
    side_effect=lambda **kwargs: kwargs,
)
def test_create_complete_epr_product__intermediate(
    mocked_complete_epr_product,
    mhs_1,
    mhs_2,
    accredited_system_1,
    accredited_system_2,
    ods_code,
    party_key,
    product_name,
    mhs_data,
    message_set_data,
    mhs_cpa_ids,
    mhs_tags,
    additional_interactions_data,
    as_device_data,
    as_tags,
    today_string,
):
    party_key_group = [
        accredited_system_1.dict(),
        mhs_1.dict(),
        mhs_2.dict(),
        accredited_system_2.dict(),
    ]

    repo = QuestionnaireRepository()
    mhs_device_questionnaire = repo.read(QuestionnaireInstance.SPINE_MHS)
    message_set_questionnaire = repo.read(QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS)
    additional_interactions_questionnaire = repo.read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    accredited_system_questionnaire = repo.read(QuestionnaireInstance.SPINE_AS)

    mhs_device_field_mapping = repo.read_field_mapping(QuestionnaireInstance.SPINE_MHS)
    message_set_field_mapping = repo.read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    accredited_system_field_mapping = repo.read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    )

    kwargs = create_complete_epr_product(
        party_key_group=party_key_group,
        mhs_device_questionnaire=mhs_device_questionnaire,
        message_set_questionnaire=message_set_questionnaire,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
        accredited_system_questionnaire=accredited_system_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
        message_set_field_mapping=message_set_field_mapping,
        accredited_system_field_mapping=accredited_system_field_mapping,
        product_team_ids={},
    )

    _additional_interactions = list(
        map(
            lambda qr: _fix_up_questionnaire(qr, today_string),
            kwargs["additional_interactions_data"],
        )
    )
    _as_device_data = list(
        map(
            lambda qr: _fix_up_questionnaire(qr, today_string), kwargs["as_device_data"]
        )
    )
    _message_set_data = list(
        map(
            lambda qr: _fix_up_questionnaire(qr, today_string),
            kwargs["message_set_data"],
        )
    )
    _mhs_data = _fix_up_questionnaire(kwargs["mhs_device_data"], today_string)

    assert _additional_interactions == additional_interactions_data
    assert _as_device_data == as_device_data
    assert _message_set_data == message_set_data
    assert _mhs_data == mhs_data

    expected_tags_1, expected_tags_2 = as_tags
    tags_1, tags_2 = kwargs["as_tags"]
    _assert_list_of_dict_equal(tags_1, expected_tags_1)
    _assert_list_of_dict_equal(tags_2, expected_tags_2)

    assert kwargs["mhs_tags"] == mhs_tags
    assert kwargs["mhs_cpa_ids"] == mhs_cpa_ids
    assert kwargs["ods_code"] == ods_code
    assert kwargs["party_key"] == party_key
    assert kwargs["product_name"] == product_name


def test_create_complete_epr_product(
    mhs_1, mhs_2, accredited_system_1, accredited_system_2
):
    party_key_group = [
        accredited_system_1.dict(),
        mhs_1.dict(),
        mhs_2.dict(),
        accredited_system_2.dict(),
    ]
    repo = QuestionnaireRepository()
    mhs_device_questionnaire = repo.read(QuestionnaireInstance.SPINE_MHS)
    message_set_questionnaire = repo.read(QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS)
    additional_interactions_questionnaire = repo.read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    accredited_system_questionnaire = repo.read(QuestionnaireInstance.SPINE_AS)

    mhs_device_field_mapping = repo.read_field_mapping(QuestionnaireInstance.SPINE_MHS)
    message_set_field_mapping = repo.read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    accredited_system_field_mapping = repo.read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    )

    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        mhs_device,
        *as_devices,
    ) = create_complete_epr_product(
        party_key_group=party_key_group,
        mhs_device_questionnaire=mhs_device_questionnaire,
        message_set_questionnaire=message_set_questionnaire,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
        accredited_system_questionnaire=accredited_system_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
        message_set_field_mapping=message_set_field_mapping,
        accredited_system_field_mapping=accredited_system_field_mapping,
        product_team_ids={},
    )

    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(mhs_device, Device)
    assert all(isinstance(device, Device) for device in as_devices)
