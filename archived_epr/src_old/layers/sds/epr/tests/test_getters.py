import json

from domain.core.questionnaire import Questionnaire
from domain.core.questionnaire.tests.test_questionnaire_v1 import VALID_SCHEMA
from domain.core.timestamp import now
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from pydantic import BaseModel
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.getters import (
    _questionnaire_response_from_field_mapping_subset,
    get_accredited_system_device_data,
    get_accredited_system_tags,
    get_additional_interactions_data,
    get_message_set_data,
    get_mhs_device_data,
    get_mhs_tags,
)


def test__questionnaire_response_from_field_mapping_subset():
    data = {"my_size": 7, "my_colour": "white"}

    class Shoe(BaseModel):
        my_size: int
        my_colour: str
        my_brand: str | None = None
        other_data: str  # to be ignored

    field_mapping = {"my_size": "size", "my_colour": "colour", "my_brand": "brand"}

    questionnaire = Questionnaire(
        name="foo", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )
    response = _questionnaire_response_from_field_mapping_subset(
        obj=Shoe(**data, other_data="something to drop").dict(),
        questionnaire=questionnaire,
        field_mapping=field_mapping,
    )
    assert response.questionnaire_name == "foo"
    assert response.questionnaire_version == "1"
    assert response.data == {"size": 7, "colour": "white"}
    assert response.created_on.date() == now().date()


def test_get_mhs_device_data(mhs_1: NhsMhs):
    mhs_device_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_MHS
    )
    mhs_device_field_mapping = QuestionnaireRepository().read_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS
    )
    mhs_data = get_mhs_device_data(
        mhs=mhs_1.dict(),
        mhs_device_questionnaire=mhs_device_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
    )
    assert mhs_data.questionnaire_name == QuestionnaireInstance.SPINE_MHS
    assert mhs_data.questionnaire_version == "1"
    assert mhs_data.data == {
        "Address": "my-mhs-endpoint",
        "Approver URP": "approver-123",
        "DNS Approver": "dns-approver-123",
        "Date Approved": "today",
        "Date DNS Approved": "yesterday",
        "Date Requested": "a week ago",
        "MHS FQDN": "my-fqdn",
        "MHS Party Key": "AAA-123456",
        "Managing Organization": "AAA",
        "Product Name": "My EPR Product",
        "Requestor URP": "requester-123",
        "MHS Manufacturer Organisation": "AAA",
    }
    assert mhs_data.created_on.date() == now().date()


def test_get_as_data(accredited_system_1: NhsAccreditedSystem):
    accredited_system_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_AS
    )
    accredited_system_field_mapping = QuestionnaireRepository().read_field_mapping(
        name=QuestionnaireInstance.SPINE_AS
    )
    as_data = get_accredited_system_device_data(
        accredited_system=accredited_system_1.dict(),
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
    )
    assert as_data.questionnaire_name == QuestionnaireInstance.SPINE_AS
    assert as_data.questionnaire_version == "1"
    assert as_data.data == {
        "ASID": "123456",
        "MHS Manufacturer Organisation": "AAA",
        "Approver URP": "approver-123",
        "Client ODS Codes": ["ABC", "CDE", "EFG"],
        "Date Approved": "today",
        "Date Requested": "a week ago",
        "ODS Code": "AAA",
        "MHS Party Key": "AAA-123456",
        "Product Key": "key-123",
        "Requestor URP": "requester-123",
        "Product Name": None,
        "Product Version": None,
        "Temp UID": None,
    }
    assert as_data.created_on.date() == now().date()


def test_get_message_set_data(mhs_1: NhsMhs, mhs_2: NhsMhs):
    message_handling_systems = [mhs_1.dict(), mhs_2.dict()]
    message_set_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_field_mapping = QuestionnaireRepository().read_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_sets = get_message_set_data(
        message_handling_systems=message_handling_systems,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
    )
    data = []
    for message_set in message_sets:
        data.append(message_set.data)
        assert (
            message_set.questionnaire_name
            == QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        assert message_set.questionnaire_version == "1"
        assert message_set.created_on.date() == now().date()

    assert data == [
        {
            "Interaction ID": "my-interaction-id",
            "MHS IN": "in-123",
            "MHS SN": "sn-123",
            "MHS CPA ID": "1wd354",
            "Product Key": "key-123",
            "Unique Identifier": "1wd354",
            "Interaction Type": "hl7",
            "MHS Is Authenticated": "none",
            "Contract Property Template Key": "key-123",
        },
        {
            "Interaction ID": "my-other-interaction-id",
            "MHS IN": "in-456",
            "MHS SN": "sn-456",
            "MHS CPA ID": "h0394j",
            "Product Key": "key-456",
            "Unique Identifier": "h0394j",
            "Interaction Type": "hl7",
            "MHS Is Authenticated": "none",
            "Contract Property Template Key": "key-456",
        },
    ]


def test_get_additional_interactions_data(
    accredited_system_1: NhsAccreditedSystem, accredited_system_2: NhsAccreditedSystem
):
    accredited_systems = [accredited_system_1.dict(), accredited_system_2.dict()]
    additional_interactions_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )

    additional_interactions = get_additional_interactions_data(
        accredited_systems=accredited_systems,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )
    data = []
    for interaction in additional_interactions:
        data.append(interaction.data)
        assert (
            interaction.questionnaire_name
            == QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        assert interaction.questionnaire_version == "1"
        assert interaction.created_on.date() == now().date()

    assert data == [
        {"Interaction ID": "interaction-id-1"},
        {"Interaction ID": "interaction-id-2"},
        {"Interaction ID": "interaction-id-4"},
    ]


def test_get_mhs_tags(mhs_1: NhsMhs, mhs_2: NhsMhs):
    message_handling_systems = [mhs_1.dict(), mhs_2.dict()]
    tags = get_mhs_tags(message_handling_systems=message_handling_systems)
    assert len(tags) == 0


def test_get_accredited_system_tags(accredited_system_1: NhsAccreditedSystem):
    tags = get_accredited_system_tags(accredited_system=accredited_system_1.dict())
    expected_tags = [
        {"nhs_id_code": "AAA", "nhs_as_svc_ia": "interaction-id-1"},
        {
            "nhs_id_code": "AAA",
            "nhs_mhs_party_key": "AAA-123456",
            "nhs_as_svc_ia": "interaction-id-1",
        },
        {"nhs_id_code": "AAA", "nhs_as_svc_ia": "interaction-id-2"},
        {
            "nhs_id_code": "AAA",
            "nhs_mhs_party_key": "AAA-123456",
            "nhs_as_svc_ia": "interaction-id-2",
        },
    ]

    for tag in tags:
        assert tag in expected_tags, f"{tag} not in expected tags"

    for tag in expected_tags:
        assert tag in tags, f"Expected {tag} in tags"

    assert len(tags) == len(expected_tags)
