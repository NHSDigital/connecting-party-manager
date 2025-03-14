import json

import pytest
from domain.core.device import Device
from domain.core.enum import Environment
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository

VALID_SHOE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "shoe-size": {
            "type": "number",
        },
        "foot": {
            "type": "string",
            "enum": ["L", "R"],
        },
    },
    "required": ["shoe-size", "foot"],
    "additionalProperties": False,
}

VALID_HEALTH_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "weight": {
            "type": "number",
        },
        "height": {
            "type": "number",
        },
    },
    "required": ["weight", "height"],
    "additionalProperties": False,
}


@pytest.fixture
def shoe_questionnaire() -> Questionnaire:
    return Questionnaire(
        name="shoe", version="1", json_schema=json.dumps(VALID_SHOE_SCHEMA)
    )


@pytest.fixture
def health_questionnaire() -> Questionnaire:
    return Questionnaire(
        name="health", version="1", json_schema=json.dumps(VALID_HEALTH_SCHEMA)
    )


@pytest.fixture
def device(
    shoe_questionnaire: Questionnaire, health_questionnaire: Questionnaire
) -> Device:
    shoe_response_1 = shoe_questionnaire.validate({"foot": "L", "shoe-size": 123})
    shoe_response_2 = shoe_questionnaire.validate({"foot": "L", "shoe-size": 345})

    health_response = health_questionnaire.validate({"weight": 123, "height": 345})

    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team_epr(name="Team")
    product = product_team.create_epr_product(name="Product")
    device = product.create_device(name="Device-1", environment=Environment.DEV)
    device.add_questionnaire_response(questionnaire_response=shoe_response_1)
    device.add_questionnaire_response(questionnaire_response=shoe_response_2)
    device.add_questionnaire_response(questionnaire_response=health_response)
    return device


@pytest.mark.integration
def test__device_repository__with_questionnaires(
    device: Device, repository: DeviceRepository
):
    repository.write(device)

    assert (
        repository.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            environment=Environment.DEV,
            id=device.id,
        )
        == device
    )


@pytest.mark.integration
def test__device_repository__with_questionnaires_and_tags(
    device: Device, repository: DeviceRepository
):
    """
    This test might look specific but it previously raised a bug due
    to model/datetime serialisation issues
    """
    device.add_tag(foo="bar")
    repository.write(device)

    assert (
        repository.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            environment=Environment.DEV,
            id=device.id,
        )
        == device
    )
