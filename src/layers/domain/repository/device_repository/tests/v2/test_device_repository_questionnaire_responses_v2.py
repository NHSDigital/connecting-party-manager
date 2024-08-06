import pytest
from domain.core.device.v2 import Device, DeviceType
from domain.core.questionnaire.v2 import Questionnaire
from domain.core.root.v2 import Root
from domain.repository.device_repository.tests.utils import devices_exactly_equal
from domain.repository.device_repository.v2 import DeviceRepository


@pytest.fixture
def shoe_questionnaire() -> Device:
    questionnaire = Questionnaire(name="shoe", version=1)
    questionnaire.add_question(
        name="foot", answer_types=(str,), mandatory=True, choices={"L", "R"}
    )
    questionnaire.add_question(name="shoe-size", answer_types=(int,), mandatory=True)
    return questionnaire


@pytest.fixture
def health_questionnaire() -> Device:
    questionnaire = Questionnaire(name="health", version=1)
    questionnaire.add_question(name="weight", answer_types=(int,), mandatory=True)
    questionnaire.add_question(name="height", answer_types=(int,), mandatory=True)
    return questionnaire


@pytest.fixture
def device(
    shoe_questionnaire: Questionnaire, health_questionnaire: Questionnaire
) -> Device:
    shoe_response_1 = shoe_questionnaire.respond(
        responses=[{"foot": ["L"]}, {"shoe-size": [123]}],
    )
    shoe_response_2 = shoe_questionnaire.respond(
        responses=[{"foot": ["L"]}, {"shoe-size": [345]}],
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
    assert repository.read(device.id) == device


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
    assert repository.read(device.id) == device


@pytest.mark.integration
def test__device_repository__modify_questionnaire_response_that_has_been_persisted(
    device: Device, repository: DeviceRepository, shoe_questionnaire: Questionnaire
):
    # Persist model before updating model
    repository.write(device)
    intermediate_device = repository.read(device.id)

    # Update the model
    questionnaire_responses = intermediate_device.questionnaire_responses
    assert len(questionnaire_responses["shoe/1"]) == 2
    (_questionnaire_response, _) = questionnaire_responses["shoe/1"].values()

    questionnaire_response = shoe_questionnaire.respond(
        responses=[{"foot": ["R"]}, {"shoe-size": [789]}]
    )
    questionnaire_response.created_on = _questionnaire_response.created_on

    intermediate_device.update_questionnaire_response(
        questionnaire_response=questionnaire_response
    )

    # Persist and verify consistency
    repository.write(intermediate_device)
    device_from_db = repository.read(intermediate_device.id)
    assert devices_exactly_equal(device_from_db, intermediate_device)
    assert not devices_exactly_equal(device_from_db, device)
    assert device_from_db.questionnaire_responses["shoe/1"][
        _questionnaire_response.created_on.isoformat()
    ].answers == [
        {"foot": ["R"]},
        {"shoe-size": [789]},
    ]

    assert device_from_db.created_on == device.created_on
    assert device_from_db.updated_on > device.updated_on
