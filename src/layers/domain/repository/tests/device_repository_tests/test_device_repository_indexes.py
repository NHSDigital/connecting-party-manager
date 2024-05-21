import pytest
from domain.core.device import Device, DeviceType
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository


@pytest.fixture
def product_team():
    org = Root.create_ods_organisation(ods_code="AB123")
    return org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )


@pytest.fixture
def shoe_questionnaire() -> Questionnaire:
    _questionnaire = Questionnaire(name="shoe", version=1)
    _questionnaire.add_question(
        name="foot", answer_types=(str,), mandatory=True, choices={"L", "R"}
    )
    _questionnaire.add_question(name="shoe-size", answer_types=(int,), mandatory=True)
    return _questionnaire


@pytest.fixture
def device_right_shoe_size_123(
    product_team: ProductTeam, shoe_questionnaire: Questionnaire
) -> Device:
    shoe_response = shoe_questionnaire.respond(
        responses=[{"foot": ["R"]}, {"shoe-size": [123]}],
    )
    device = product_team.create_device(name="Device-1", type=DeviceType.PRODUCT)
    device.add_questionnaire_response(questionnaire_response=shoe_response)
    device.add_index(questionnaire_id=shoe_questionnaire.id, question_name="foot")
    device.add_index(questionnaire_id=shoe_questionnaire.id, question_name="shoe-size")
    return device


@pytest.fixture
def device_left_shoe_size_123(
    product_team: ProductTeam, shoe_questionnaire: Questionnaire
) -> Device:
    shoe_response = shoe_questionnaire.respond(
        responses=[{"foot": ["L"]}, {"shoe-size": [123]}],
    )
    device = product_team.create_device(name="Device-2", type=DeviceType.PRODUCT)
    device.add_questionnaire_response(questionnaire_response=shoe_response)
    device.add_index(questionnaire_id=shoe_questionnaire.id, question_name="foot")
    device.add_index(questionnaire_id=shoe_questionnaire.id, question_name="shoe-size")
    return device


@pytest.mark.integration
def test__device_repository__query_by_index__find_right_shoes(
    device_right_shoe_size_123: Device,
    device_left_shoe_size_123: Device,
    repository: DeviceRepository,
):
    repository.write(device_right_shoe_size_123)
    repository.write(device_left_shoe_size_123)

    (device,) = repository.read_by_index(
        questionnaire_id="shoe/1", question_name="foot", value="R"
    )
    assert device.id == device_right_shoe_size_123.id
    assert device.indexes == device_right_shoe_size_123.indexes


@pytest.mark.integration
def test__device_repository__query_by_index__find_left_shoes(
    device_right_shoe_size_123: Device,
    device_left_shoe_size_123: Device,
    repository: DeviceRepository,
):
    repository.write(device_right_shoe_size_123)
    repository.write(device_left_shoe_size_123)

    (device,) = repository.read_by_index(
        questionnaire_id="shoe/1", question_name="foot", value="L"
    )
    assert device.id == device_left_shoe_size_123.id
    assert device.indexes == device_left_shoe_size_123.indexes


@pytest.mark.integration
def test__device_repository__query_by_index__find_shoes_by_size_int(
    device_right_shoe_size_123: Device,
    device_left_shoe_size_123: Device,
    repository: DeviceRepository,
):
    repository.write(device_right_shoe_size_123)
    repository.write(device_left_shoe_size_123)

    (device_1, device_2) = repository.read_by_index(
        questionnaire_id="shoe/1", question_name="shoe-size", value=123
    )
    assert {device_1.id, device_2.id} == {
        device_left_shoe_size_123.id,
        device_right_shoe_size_123.id,
    }
    assert {*device_2.indexes, *device_1.indexes} == {
        *device_left_shoe_size_123.indexes,
        *device_right_shoe_size_123.indexes,
    }


@pytest.mark.integration
def test__device_repository__query_by_index__find_shoes_by_size_str(
    device_right_shoe_size_123: Device,
    device_left_shoe_size_123: Device,
    repository: DeviceRepository,
):
    repository.write(device_right_shoe_size_123)
    repository.write(device_left_shoe_size_123)

    (device_1, device_2) = repository.read_by_index(
        questionnaire_id="shoe/1", question_name="shoe-size", value="123"
    )
    assert {device_1.id, device_2.id} == {
        device_left_shoe_size_123.id,
        device_right_shoe_size_123.id,
    }
    assert {*device_2.indexes, *device_1.indexes} == {
        *device_left_shoe_size_123.indexes,
        *device_right_shoe_size_123.indexes,
    }


@pytest.mark.integration
def test__device_repository__query_by_index__empty_result(
    device_right_shoe_size_123: Device,
    device_left_shoe_size_123: Device,
    repository: DeviceRepository,
):
    repository.write(device_right_shoe_size_123)
    repository.write(device_left_shoe_size_123)
    result = repository.read_by_index(
        questionnaire_id="shoe/1", question_name="shoe-size", value="345"
    )
    assert result == []
