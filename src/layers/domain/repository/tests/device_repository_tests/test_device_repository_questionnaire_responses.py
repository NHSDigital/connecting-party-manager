import pytest
from domain.core.device import Device, DeviceType
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository

from .conftest import devices_exactly_equal


@pytest.fixture
def device() -> Device:
    shoe_questionnaire = Questionnaire(name="shoe", version=1)
    shoe_questionnaire.add_question(
        name="foot", answer_types=(str,), mandatory=True, choices={"L", "R"}
    )
    shoe_questionnaire.add_question(
        name="shoe-size", answer_types=(int,), mandatory=True
    )
    shoe_response_1 = shoe_questionnaire.respond(
        responses=[{"foot": ["L"]}, {"shoe-size": [123]}],
    )
    shoe_response_2 = shoe_questionnaire.respond(
        responses=[{"foot": ["L"]}, {"shoe-size": [345]}],
    )

    health_questionnaire = Questionnaire(name="health", version=1)
    health_questionnaire.add_question(
        name="weight", answer_types=(int,), mandatory=True
    )
    health_questionnaire.add_question(
        name="height", answer_types=(int,), mandatory=True
    )
    health_response = health_questionnaire.respond(
        responses=[{"weight": [123]}, {"height": [345]}]
    )

    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    device = product_team.create_device(name="Device-1", device_type=DeviceType.PRODUCT)
    device.add_questionnaire_response(questionnaire_response=shoe_response_1)
    device.add_questionnaire_response(questionnaire_response=shoe_response_2)
    device.add_questionnaire_response(questionnaire_response=health_response)
    return device


@pytest.mark.integration
def test__device_repository__with_questionnaires(
    device: Device, repository: DeviceRepository
):
    repository.write(device)
    assert repository.read(id=device.id) == device


@pytest.mark.integration
def test__device_repository__delete_questionnaire_response_that_has_been_persisted(
    device: Device, repository: DeviceRepository
):
    def _sum_array_lengths(obj: dict[str, list]):
        return sum(map(len, obj.values()))

    # Persist model before deleting from model
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(id=device.id)
    _responses_before = _sum_array_lengths(device.questionnaire_responses)
    responses_before = _sum_array_lengths(intermediate_device.questionnaire_responses)
    assert intermediate_device == device
    assert _responses_before == responses_before

    # Delete from the model pulled down from the db, and then persist
    intermediate_device.delete_questionnaire_response(
        questionnaire_id="health/1", questionnaire_response_index=0
    )
    responses_after = _sum_array_lengths(intermediate_device.questionnaire_responses)
    repository.write(intermediate_device)
    assert responses_after == responses_before - 1

    # Verify that we get the correct result back
    device_from_db = repository.read(id=device.id)
    assert devices_exactly_equal(device_from_db, intermediate_device)
    assert not devices_exactly_equal(device_from_db, device)


@pytest.mark.integration
def test__device_repository__modify_questionnaire_response_that_has_been_persisted(
    device: Device, repository: DeviceRepository
):
    # Persist model before updating model
    repository.write(device)
    intermediate_device = repository.read(id=device.id)

    # Update the model
    questionnaire_responses = intermediate_device.questionnaire_responses
    shoe_questionnaire = questionnaire_responses["shoe/1"][0].questionnaire
    questionnaire_response = shoe_questionnaire.respond(
        responses=[{"foot": ["R"]}, {"shoe-size": [789]}]
    )
    intermediate_device.update_questionnaire_response(
        questionnaire_response_index=0, questionnaire_response=questionnaire_response
    )

    # Persist and verify consistency
    repository.write(intermediate_device)
    device_from_db = repository.read(id=intermediate_device.id)
    assert devices_exactly_equal(device_from_db, intermediate_device)
    assert not devices_exactly_equal(device_from_db, device)
    assert device_from_db.questionnaire_responses["shoe/1"][0].responses == [
        {"foot": ["R"]},
        {"shoe-size": [789]},
    ]
