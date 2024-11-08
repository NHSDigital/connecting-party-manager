import json

from domain.repository.device_repository.tests.utils import devices_exactly_equal
import pytest
from domain.core.device.v3 import Device
from domain.core.questionnaire.v3 import Questionnaire
from domain.core.root.v3 import Root
from domain.repository.device_repository.v3 import DeviceRepository

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
    product_team = org.create_product_team(name="Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-1")
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
            id=device.id,
        )
        == device
    )


@pytest.mark.integration
def test__device_repository__modify_questionnaire_response_that_has_been_persisted(
    device: Device, repository: DeviceRepository, shoe_questionnaire: Questionnaire
):
    # Persist model before updating model
    repository.write(device)
    intermediate_device = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )

    # Update the model
    questionnaire_responses = intermediate_device.questionnaire_responses
    assert len(questionnaire_responses["shoe/1"]) == 2
    (_questionnaire_response, _) = questionnaire_responses["shoe/1"]

    questionnaire_response = shoe_questionnaire.validate(
        {"foot": "R", "shoe-size": 789}
    )
    questionnaire_response.created_on = _questionnaire_response.created_on

    intermediate_device.update_questionnaire_response(
        questionnaire_response=questionnaire_response
    )

    # Persist and verify consistency
    repository.write(intermediate_device)
    device_from_db = repository.read(
        product_team_id=intermediate_device.product_team_id,
        product_id=intermediate_device.product_id,
        id=intermediate_device.id,
    )
    assert devices_exactly_equal(device_from_db, intermediate_device)
    assert not devices_exactly_equal(device_from_db, device)
    assert device_from_db.questionnaire_responses["shoe/1"][-1].data == {
        "foot": ["R"],
        "shoe-size": [789],
    }

    assert device_from_db.created_on == device.created_on
    assert device_from_db.updated_on > device.updated_on
