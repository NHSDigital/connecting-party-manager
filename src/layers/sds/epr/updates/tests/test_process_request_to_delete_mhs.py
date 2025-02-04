import pytest
from domain.core.device.v1 import Device, DeviceKeyDeletedEvent
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team.v1 import ProductTeam
from domain.core.root.v1 import Root
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.bulk_create.tests.conftest import mhs_1, mhs_2  # noqa
from sds.epr.creators import create_message_sets, create_mhs_device
from sds.epr.getters import get_message_set_data, get_mhs_device_data
from sds.epr.updates.change_request_processors import process_request_to_delete_mhs
from sds.epr.updates.etl_device import DeviceHardDeletedEvent

from test_helpers.dynamodb import mock_table  # noqa


@pytest.fixture
def product_team():
    ods_org = Root.create_ods_organisation(ods_code="AAA")
    return ods_org.create_product_team_epr(name="my product team")


@pytest.fixture
def product(product_team: ProductTeam):
    return product_team.create_epr_product(name="my product")


@pytest.fixture
def message_sets_with_two_cpa_ids(product: EprProduct, mhs_1: NhsMhs, mhs_2: NhsMhs):
    message_set_data = get_message_set_data(
        message_handling_systems=[mhs_1.dict(), mhs_2.dict()],
        message_set_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
        message_set_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
    )
    return create_message_sets(
        product=product,
        party_key="123",
        message_set_data=message_set_data,
    )


@pytest.fixture
def mhs_device_with_two_cpa_ids(
    mhs_1: NhsMhs,
    message_sets_with_two_cpa_ids: DeviceReferenceData,
    product: EprProduct,
):
    mhs_device_data = get_mhs_device_data(
        mhs=mhs_1.dict(),
        mhs_device_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_MHS
        ),
        mhs_device_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_MHS
        ),
    )
    return create_mhs_device(
        product=product,
        party_key="123",
        cpa_ids=["1wd354", "h0394j"],
        mhs_device_data=mhs_device_data,
        message_sets_id=message_sets_with_two_cpa_ids.id,
    )


@pytest.fixture
def message_sets_with_one_cpa_id(product: EprProduct, mhs_1: NhsMhs):
    message_set_data = get_message_set_data(
        message_handling_systems=[mhs_1.dict()],
        message_set_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
        message_set_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
    )
    return create_message_sets(
        product=product,
        party_key="123",
        message_set_data=message_set_data,
    )


@pytest.fixture
def mhs_device_with_one_cpa_id(
    mhs_1: NhsMhs,
    message_sets_with_one_cpa_id: DeviceReferenceData,
    product: EprProduct,
):
    mhs_device_data = get_mhs_device_data(
        mhs=mhs_1.dict(),
        mhs_device_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_MHS
        ),
        mhs_device_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_MHS
        ),
    )
    return create_mhs_device(
        product=product,
        party_key="123",
        cpa_ids=["1wd354"],
        mhs_device_data=mhs_device_data,
        message_sets_id=message_sets_with_one_cpa_id.id,
    )


def test_process_request_to_delete_mhs__there_are_other_cpa_id_keys_so_dont_delete_device(
    mhs_device_with_two_cpa_ids: Device,
    message_sets_with_two_cpa_ids: DeviceReferenceData,
):
    table_name = "my-table"
    with mock_table(table_name=table_name) as client:
        device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=table_name, dynamodb_client=client
        )

        device_repo.write(mhs_device_with_two_cpa_ids)
        device_reference_data_repo.write(message_sets_with_two_cpa_ids)

        etl_device, modified_message_sets = process_request_to_delete_mhs(
            device=mhs_device_with_two_cpa_ids,
            cpa_id_to_delete="1wd354",
            device_reference_data_repository=device_reference_data_repo,
        )

    assert etl_device.events == [
        DeviceKeyDeletedEvent(
            deleted_key={"key_type": "cpa_id", "key_value": "1wd354"},
            id=str(mhs_device_with_two_cpa_ids.id),
            keys=[{"key_type": "cpa_id", "key_value": "h0394j"}],
            tags=[],
            updated_on=etl_device.events[0].updated_on,
        )
    ]

    (questionnaire_updated_event,) = modified_message_sets.events
    assert isinstance(questionnaire_updated_event, QuestionnaireResponseUpdatedEvent)
    assert questionnaire_updated_event.id == str(message_sets_with_two_cpa_ids.id)

    updated_message_sets_questionnaires = (
        questionnaire_updated_event.questionnaire_responses["spine_mhs_message_sets/1"]
    )
    assert len(updated_message_sets_questionnaires) == 1
    (remaining_message_set,) = updated_message_sets_questionnaires

    second_original_message_set_questionnaire = (
        message_sets_with_two_cpa_ids.questionnaire_responses[
            "spine_mhs_message_sets/1"
        ][1]
    )
    assert (
        remaining_message_set["data"] == second_original_message_set_questionnaire.data
    )


def test_process_request_to_delete_mhs__there_are_no_more_cpa_id_keys_so_do_delete_device(
    mhs_device_with_one_cpa_id: Device,
    message_sets_with_one_cpa_id: DeviceReferenceData,
):
    table_name = "my-table"
    with mock_table(table_name=table_name) as client:
        device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=table_name, dynamodb_client=client
        )

        device_repo.write(mhs_device_with_one_cpa_id)
        device_reference_data_repo.write(message_sets_with_one_cpa_id)

        etl_device, modified_message_sets = process_request_to_delete_mhs(
            device=mhs_device_with_one_cpa_id,
            cpa_id_to_delete="1wd354",
            device_reference_data_repository=device_reference_data_repo,
        )

    assert etl_device.events == [
        DeviceKeyDeletedEvent(
            deleted_key={"key_type": "cpa_id", "key_value": "1wd354"},
            id=str(mhs_device_with_one_cpa_id.id),
            keys=[],
            tags=[],
            updated_on=etl_device.events[0].updated_on,
        ),
        DeviceHardDeletedEvent(
            id=str(mhs_device_with_one_cpa_id.id),
            keys=[],
            tags=[],
        ),
    ]

    (questionnaire_updated_event,) = modified_message_sets.events
    assert isinstance(questionnaire_updated_event, QuestionnaireResponseUpdatedEvent)
    assert questionnaire_updated_event.id == str(message_sets_with_one_cpa_id.id)

    modified_message_sets_data = questionnaire_updated_event.questionnaire_responses[
        "spine_mhs_message_sets/1"
    ]
    assert len(modified_message_sets_data) == 0
