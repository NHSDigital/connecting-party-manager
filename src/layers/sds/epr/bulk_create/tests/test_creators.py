import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.device import Device
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.product_team import ProductTeam
from domain.core.timestamp import now
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from pydantic import ValidationError
from sds.epr.bulk_create.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.constants import EXCEPTIONAL_ODS_CODES


@pytest.fixture(scope="module")
def today_string():
    return now().date().isoformat()


@pytest.fixture(scope="module")
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture(scope="module")
def party_key():
    return "AAA-123456"


@pytest.fixture(scope="module")
def product(product_team, party_key):
    return create_epr_product(
        product_team=product_team, product_name="My Product", party_key=party_key
    )


@pytest.fixture(scope="module")
def message_sets(product, party_key):
    questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_data = [
        questionnaire.validate(data=_raw_message_set_data)
        for _raw_message_set_data in (
            {
                "MHS SN": "sn-123",
                "MHS IN": "in-123",
                "Interaction ID": "sn-123:in-123",
                "MHS CPA ID": "AAA-123456:sn-123:in-123",
                "Unique Identifier": "AAA-123456:sn-123:in-123",
            },
            {
                "MHS SN": "sn-456",
                "MHS IN": "in-456",
                "Interaction ID": "sn-456:in-456",
                "MHS CPA ID": "AAA-123456:sn-456:in-456",
                "Unique Identifier": "AAA-123456:sn-456:in-456",
            },
        )
    ]
    return create_message_sets(
        product=product, party_key=party_key, message_set_data=message_set_data
    )


@pytest.fixture(scope="module")
def mhs_tags():
    return [
        {
            "nhs_id_code": "AAA",
        },
        {
            "nhs_mhs_svc_ia": "my-interaction-id",
        },
        {
            "nhs_mhs_party_key": "AAA-123456",
        },
        {
            "nhs_id_code": "AAA",
            "nhs_mhs_svc_ia": "my-interaction-id",
        },
    ]


@pytest.fixture(scope="module")
def mhs_device(product, party_key, message_sets: DeviceReferenceData, mhs_tags):
    cpa_ids = ["er3243", "23143a"]
    questionnaire = QuestionnaireRepository().read(name=QuestionnaireInstance.SPINE_MHS)
    mhs_device_data = questionnaire.validate(
        data={
            "Address": "my-mhs-endpoint",
            "Approver URP": "approver-123",
            "DNS Approver": "dns-approver-123",
            "Date Approved": "today",
            "Date DNS Approved": "yesterday",
            "Date Requested": "a week ago",
            "MHS FQDN": "my-fqdn",
            "MHS Party key": "AAA-123456",
            "Managing Organization": "AAA",
            "Product Name": "My EPR Product",
            "Requestor URP": "requester-123",
            "MHS Manufacturer Organisation": "AAA",
        }
    )
    return create_mhs_device(
        product=product,
        party_key=party_key,
        mhs_device_data=mhs_device_data,
        cpa_ids=cpa_ids,
        message_sets_id=str(message_sets.id),
        mhs_tags=mhs_tags,
    )


@pytest.fixture(scope="module")
def additional_interactions(product, party_key):
    questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    additional_interactions_data = [
        questionnaire.validate(data=_raw_additional_interactions_data)
        for _raw_additional_interactions_data in (
            {"Interaction ID": "interaction-id-1"},
            {"Interaction ID": "interaction-id-2"},
            {"Interaction ID": "interaction-id-4"},
        )
    ]

    return create_additional_interactions(
        product=product,
        party_key=party_key,
        additional_interactions_data=additional_interactions_data,
    )


@pytest.fixture(scope="module")
def as_device(
    product,
    party_key,
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
        party_key=party_key,
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


def test_create_epr_product_team(product_team: ProductTeam, today_string: str):
    _product_team = product_team.state()
    assert _product_team.pop("created_on").startswith(today_string)
    assert _product_team.pop("id").startswith("AAA.")
    assert _product_team == {
        "deleted_on": None,
        "keys": [
            {
                "key_type": "epr_id",
                "key_value": "EPR-AAA",
            },
        ],
        "name": "AAA (EPR)",
        "ods_code": "AAA",
        "status": "active",
        "updated_on": None,
    }


@pytest.mark.parametrize("ods_code", EXCEPTIONAL_ODS_CODES)
def test_create_epr_product_team_exceptional_ods_codes(
    ods_code: str, today_string: str
):
    product_team = create_epr_product_team(ods_code)
    _product_team = product_team.state()
    assert _product_team.pop("created_on").startswith(today_string)
    assert _product_team.pop("id").startswith(f"{ods_code}.")
    assert _product_team == {
        "deleted_on": None,
        "keys": [
            {
                "key_type": "epr_id",
                "key_value": f"EPR-{ods_code}",
            },
        ],
        "name": f"{ods_code} (EPR)",
        "ods_code": ods_code,
        "status": "active",
        "updated_on": None,
    }


def test_create_epr_product_team_bad_ods_codes():
    with pytest.raises(ValidationError):
        create_epr_product_team("21h32jh4282")


def test_create_epr_product(
    product_team: ProductTeam, product: CpmProduct, today_string: str
):
    _product = product.state()
    _product.pop("id")
    assert _product.pop("created_on").startswith(today_string)
    assert _product.pop("updated_on").startswith(today_string)
    assert _product == {
        "deleted_on": None,
        "keys": [
            {
                "key_type": "party_key",
                "key_value": "AAA-123456",
            },
        ],
        "name": "My Product",
        "ods_code": "AAA",
        "product_team_id": product_team.id,
        "status": "active",
    }


def test_create_message_sets(
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    today_string: str,
):
    _message_sets = message_sets.state()
    responses = _message_sets["questionnaire_responses"]["spine_mhs_message_sets/1"]
    assert _message_sets.pop("created_on").startswith(today_string)
    assert _message_sets.pop("updated_on").startswith(today_string)
    assert responses[0].pop("created_on").startswith(today_string)
    assert responses[1].pop("created_on").startswith(today_string)

    _message_sets.pop("id")
    responses[0].pop("id")
    responses[1].pop("id")

    assert _message_sets == {
        "deleted_on": None,
        "name": "AAA-123456 - MHS Message Sets",
        "ods_code": "AAA",
        "product_id": str(product.id),
        "product_team_id": product_team.id,
        "status": "active",
        "questionnaire_responses": {
            "spine_mhs_message_sets/1": [
                {
                    "data": {
                        "MHS SN": "sn-123",
                        "MHS IN": "in-123",
                        "Interaction ID": "sn-123:in-123",
                        "MHS CPA ID": "AAA-123456:sn-123:in-123",
                        "Unique Identifier": "AAA-123456:sn-123:in-123",
                    },
                    "questionnaire_name": "spine_mhs_message_sets",
                    "questionnaire_version": "1",
                },
                {
                    "data": {
                        "MHS SN": "sn-456",
                        "MHS IN": "in-456",
                        "Interaction ID": "sn-456:in-456",
                        "MHS CPA ID": "AAA-123456:sn-456:in-456",
                        "Unique Identifier": "AAA-123456:sn-456:in-456",
                    },
                    "questionnaire_name": "spine_mhs_message_sets",
                    "questionnaire_version": "1",
                },
            ],
        },
    }


def test_create_mhs_device(
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    mhs_device: Device,
    today_string: str,
):
    _mhs_device = mhs_device.state()
    assert _mhs_device.pop("created_on").startswith(today_string)
    assert _mhs_device.pop("updated_on").startswith(today_string)

    responses = _mhs_device["questionnaire_responses"]["spine_mhs/1"]
    assert responses[0].pop("created_on").startswith(today_string)

    _mhs_device.pop("id")
    responses[0].pop("id")

    tags = _mhs_device.pop("tags")
    expected_tags = [
        [["nhs_id_code", "aaa"], ["nhs_mhs_svc_ia", "my-interaction-id"]],
        [["nhs_id_code", "aaa"]],
        [["nhs_mhs_party_key", "aaa-123456"]],
        [["nhs_mhs_svc_ia", "my-interaction-id"]],
    ]
    assert all(t in expected_tags for t in tags)
    assert all(t in tags for t in expected_tags)
    assert len(tags) == len(expected_tags)

    assert _mhs_device == {
        "deleted_on": None,
        "device_reference_data": {
            str(message_sets.id): ["*"],
        },
        "keys": [
            {"key_type": "cpa_id", "key_value": "er3243"},
            {"key_type": "cpa_id", "key_value": "23143a"},
        ],
        "name": "AAA-123456 - Message Handling System",
        "ods_code": "AAA",
        "product_id": str(product.id),
        "product_team_id": product_team.id,
        "questionnaire_responses": {
            "spine_mhs/1": [
                {
                    "data": {
                        "Address": "my-mhs-endpoint",
                        "Approver URP": "approver-123",
                        "DNS Approver": "dns-approver-123",
                        "Date Approved": "today",
                        "Date DNS Approved": "yesterday",
                        "Date Requested": "a week ago",
                        "MHS FQDN": "my-fqdn",
                        "MHS Party key": "AAA-123456",
                        "Managing Organization": "AAA",
                        "Product Name": "My EPR Product",
                        "Requestor URP": "requester-123",
                        "MHS Manufacturer Organisation": "AAA",
                    },
                    "questionnaire_name": "spine_mhs",
                    "questionnaire_version": "1",
                },
            ],
        },
        "status": "active",
    }


def test_create_additional_interactions(
    product_team: ProductTeam,
    product: CpmProduct,
    additional_interactions: DeviceReferenceData,
    today_string: str,
):
    _additional_interactions = additional_interactions.state()
    responses = _additional_interactions["questionnaire_responses"][
        "spine_as_additional_interactions/1"
    ]
    assert _additional_interactions.pop("created_on").startswith(today_string)
    assert _additional_interactions.pop("updated_on").startswith(today_string)
    assert responses[0].pop("created_on").startswith(today_string)
    assert responses[1].pop("created_on").startswith(today_string)
    assert responses[2].pop("created_on").startswith(today_string)

    _additional_interactions.pop("id")
    responses[0].pop("id")
    responses[1].pop("id")
    responses[2].pop("id")

    assert _additional_interactions == {
        "deleted_on": None,
        "name": "AAA-123456 - AS Additional Interactions",
        "ods_code": "AAA",
        "product_id": str(product.id),
        "product_team_id": product_team.id,
        "status": "active",
        "questionnaire_responses": {
            "spine_as_additional_interactions/1": [
                {
                    "data": {
                        "Interaction ID": "interaction-id-1",
                    },
                    "questionnaire_name": "spine_as_additional_interactions",
                    "questionnaire_version": "1",
                },
                {
                    "data": {
                        "Interaction ID": "interaction-id-2",
                    },
                    "questionnaire_name": "spine_as_additional_interactions",
                    "questionnaire_version": "1",
                },
                {
                    "data": {
                        "Interaction ID": "interaction-id-4",
                    },
                    "questionnaire_name": "spine_as_additional_interactions",
                    "questionnaire_version": "1",
                },
            ],
        },
    }


def test_create_as_device(
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    additional_interactions: DeviceReferenceData,
    as_device: Device,
    today_string: str,
):
    _as_device = as_device.state()
    assert _as_device.pop("created_on").startswith(today_string)
    assert _as_device.pop("updated_on").startswith(today_string)

    responses = _as_device["questionnaire_responses"]["spine_as/1"]
    assert responses[0].pop("created_on").startswith(today_string)

    _as_device.pop("id")
    responses[0].pop("id")

    tags = _as_device.pop("tags")
    expected_tags = [
        [
            ["nhs_as_client", "cde"],
            ["nhs_as_svc_ia", "interaction-id-1"],
            ["nhs_mhs_manufacturer_org", "aaa"],
            ["nhs_mhs_party_key", "aaa-123456"],
        ],
        [
            ["nhs_as_client", "abc"],
            ["nhs_as_svc_ia", "interaction-id-1"],
            ["nhs_mhs_party_key", "aaa-123456"],
        ],
    ]
    assert all(t in expected_tags for t in tags)
    assert all(t in tags for t in expected_tags)
    assert len(tags) == len(expected_tags)

    assert _as_device == {
        "deleted_on": None,
        "device_reference_data": {
            str(message_sets.id): ["*.Interaction ID"],
            str(additional_interactions.id): ["*.Interaction ID"],
        },
        "keys": [
            {"key_type": "accredited_system_id", "key_value": "123456"},
        ],
        "name": "AAA-123456/123456 - Accredited System",
        "ods_code": "AAA",
        "product_id": str(product.id),
        "product_team_id": product_team.id,
        "questionnaire_responses": {
            "spine_as/1": [
                {
                    "data": {
                        "ASID": "123456",
                        "Approver URP": "approver-123",
                        "Client ODS Codes": [
                            "ABC",
                            "CDE",
                            "EFG",
                        ],
                        "Date Approved": "today",
                        "Date Requested": "a week ago",
                        "MHS Manufacturer Organisation": "AAA",
                        "ODS Code": "AAA",
                        "Party Key": "AAA-123456",
                        "Product Key": "key-123",
                        "Requestor URP": "requester-123",
                    },
                    "questionnaire_name": "spine_as",
                    "questionnaire_version": "1",
                },
            ],
        },
        "status": "active",
    }
