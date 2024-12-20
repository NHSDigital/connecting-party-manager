import pytest
from domain.core.cpm_product.v1 import (
    CpmProduct,
    CpmProductCreatedEvent,
    CpmProductKeyAddedEvent,
)
from domain.core.device.v1 import (
    Device,
    DeviceCreatedEvent,
    DeviceKeyAddedEvent,
    DeviceReferenceDataIdAddedEvent,
    DeviceTagsAddedEvent,
)
from domain.core.device.v1 import (
    QuestionnaireResponseUpdatedEvent as DeviceQuestionnaireUpdatedEvent,
)
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
)
from domain.core.device_reference_data.v1 import (
    QuestionnaireResponseUpdatedEvent as DrdQuestionnaireUpdatedEvent,
)
from domain.core.product_team.v1 import ProductTeam, ProductTeamCreatedEvent
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from domain.repository.repository.v1 import Repository
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.bulk_create.tests.conftest import accredited_system_1, mhs_1  # noqa
from sds.epr.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
)
from sds.epr.getters import (
    get_accredited_system_device_data,
    get_accredited_system_tags,
    get_additional_interactions_data,
    get_message_set_data,
)
from sds.epr.updates.change_request_processors import process_request_to_add_as

from test_helpers.dynamodb import mock_table

TABLE_NAME = "foo"


@pytest.fixture
def input_questionnaires():
    return dict(
        accredited_system_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_AS
        ),
        additional_interactions_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
    )


@pytest.fixture
def repository():
    with mock_table(TABLE_NAME) as client:
        repo_kwargs = dict(table_name=TABLE_NAME, dynamodb_client=client)
        yield {
            "product_team_repository": ProductTeamRepository(**repo_kwargs),
            "product_repository": CpmProductRepository(**repo_kwargs),
            "device_repository": DeviceRepository(**repo_kwargs),
            "device_reference_data_repository": DeviceReferenceDataRepository(
                **repo_kwargs
            ),
        }


@pytest.fixture
def mhs(mhs_1: NhsMhs):
    """Alias to fixture from sds.epr.bulk_create.tests.conftest"""
    return mhs_1.dict()


@pytest.fixture
def accredited_system(accredited_system_1: NhsMhs):
    """Alias to fixture from sds.epr.bulk_create.tests.conftest"""
    return accredited_system_1.dict()


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
        ]
    ]


@pytest.fixture
def another_accredited_system(accredited_system):
    accredited_system["nhs_as_svc_ia"] = ["another-interaction-id"]
    accredited_system["unique_identifier"] = "456789"
    return accredited_system


@pytest.fixture
def as_tags_2():
    return [
        [
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "another-interaction-id",
            },
            {
                "nhs_id_code": "AAA",
                "nhs_as_svc_ia": "another-interaction-id",
                "nhs_mhs_party_key": "AAA-123456",
            },
        ]
    ]


@pytest.fixture
def initial_product_team(accredited_system_1: NhsMhs):
    return create_epr_product_team(
        ods_code=accredited_system_1.nhs_mhs_manufacturer_org
    )


@pytest.fixture
def initial_product(accredited_system_1: NhsMhs, initial_product_team):
    return create_epr_product(
        product_team=initial_product_team,
        product_name=accredited_system_1.unique_identifier,
        party_key=accredited_system_1.nhs_mhs_party_key,
    )


@pytest.fixture
def empty_message_sets(accredited_system_1: NhsMhs, initial_product):
    return create_message_sets(
        product=initial_product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        message_set_data=[],
    )


@pytest.fixture
def non_empty_message_sets(mhs: dict, accredited_system_1: NhsMhs, initial_product):
    mhs["nhs_mhs_svc_ia"] = "interaction-id-1"
    message_set_data = get_message_set_data(
        message_handling_systems=[mhs],
        message_set_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
        message_set_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
    )
    return create_message_sets(
        product=initial_product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        message_set_data=message_set_data,
    )


@pytest.fixture
def initial_additional_interactions(
    accredited_system_1: NhsAccreditedSystem, initial_product
):
    additional_interactions_data = get_additional_interactions_data(
        accredited_systems=[accredited_system_1.dict()],
        additional_interactions_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
    )
    return create_additional_interactions(
        product=initial_product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        additional_interactions_data=additional_interactions_data,
    )


@pytest.fixture
def initial_accredited_system_device(
    accredited_system: dict,
    accredited_system_1: NhsMhs,
    initial_product,
    initial_additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
):
    accredited_system_device_data = get_accredited_system_device_data(
        accredited_system=accredited_system,
        accredited_system_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_AS
        ),
    )
    as_tags = get_accredited_system_tags(accredited_system)

    return create_as_device(
        product=initial_product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        asid=accredited_system_1.unique_identifier,
        as_device_data=accredited_system_device_data,
        message_sets_id=empty_message_sets.id,
        additional_interactions_id=initial_additional_interactions.id,
        as_tags=as_tags,
    )


@pytest.fixture
def another_accredited_system_device(
    another_accredited_system: dict,
    accredited_system_1: NhsMhs,
    initial_product,
    initial_additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
):
    accredited_system_device_data = get_accredited_system_device_data(
        accredited_system=another_accredited_system,
        accredited_system_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_AS
        ),
    )
    as_tags = get_accredited_system_tags(another_accredited_system)

    return create_as_device(
        product=initial_product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        asid=another_accredited_system["unique_identifier"],
        as_device_data=accredited_system_device_data,
        message_sets_id=empty_message_sets.id,
        additional_interactions_id=initial_additional_interactions.id,
        as_tags=as_tags,
    )


@pytest.fixture
def expected_product_team(initial_product_team):
    return initial_product_team


@pytest.fixture
def expected_product(initial_product):
    return initial_product


@pytest.fixture
def expected_empty_message_sets(empty_message_sets):
    return empty_message_sets


@pytest.fixture
def expected_non_empty_message_sets(non_empty_message_sets):
    return non_empty_message_sets


@pytest.fixture
def expected_additional_interactions(initial_additional_interactions):
    return initial_additional_interactions


@pytest.fixture
def expected_device(initial_accredited_system_device):
    return initial_accredited_system_device


@pytest.fixture
def expected_device_tags(as_tags):
    return as_tags


@pytest.fixture
def expected_additional_device(another_accredited_system_device):
    return another_accredited_system_device


@pytest.fixture
def expected_additional_device_tags(as_tags_2):
    return as_tags_2


def equivalent_questionnaire_responses[
    item_type: Device | DeviceReferenceData
](new_item: item_type, old_item: item_type) -> bool:
    questionnaires = old_item.questionnaire_responses.keys()
    assert new_item.questionnaire_responses.keys() == questionnaires
    for q in questionnaires:
        new_questionnaire_responses = new_item.questionnaire_responses[q]
        old_questionnaire_responses = old_item.questionnaire_responses[q]
        assert len(old_questionnaire_responses) == len(new_questionnaire_responses)
        for new_qr, old_qr in zip(
            new_questionnaire_responses, old_questionnaire_responses
        ):
            assert new_qr.data == old_qr.data
    return True


def equivalent[
    item_type: ProductTeam | CpmProduct | Device | DeviceReferenceData
](new_item: item_type, old_item: item_type) -> bool:
    assert new_item.id != old_item.id
    assert new_item.name == old_item.name
    assert new_item.created_on > old_item.created_on
    if old_item.updated_on:
        assert new_item.updated_on > old_item.updated_on

    if not isinstance(old_item, DeviceReferenceData):
        assert new_item.keys == old_item.keys

    if isinstance(old_item, (Device, DeviceReferenceData)):
        assert equivalent_questionnaire_responses(new_item=new_item, old_item=old_item)

    if isinstance(old_item, Device):
        assert new_item.tags == old_item.tags
        assert list(new_item.device_reference_data.values()) == list(
            old_item.device_reference_data.values()
        )

    return True


def test_process_request_to_add_as_no_initial_state(
    accredited_system: dict,
    repository: dict,
    input_questionnaires: dict,
    expected_product_team,
    expected_product,
    expected_empty_message_sets,
    expected_additional_interactions,
    expected_device,
):
    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=accredited_system, **repository, **input_questionnaires
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)

    (product_team_created_event,) = product_team.events
    (product_created_event, product_key_added_event) = product.events
    (mhs_device_ref_data_created_event,) = message_sets.events
    (
        accredited_system_device_ref_data_created_event,
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        accredited_system_device_ref_data_questionnaire_updated_event_2,
    ) = additional_interactions.events
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events
    assert isinstance(product_team_created_event, ProductTeamCreatedEvent)
    assert isinstance(product_created_event, CpmProductCreatedEvent)
    assert isinstance(product_key_added_event, CpmProductKeyAddedEvent)
    assert isinstance(
        mhs_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_2,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )
    assert equivalent(product_team, expected_product_team)
    assert equivalent(product, expected_product)
    assert equivalent(message_sets, expected_empty_message_sets)
    assert equivalent(additional_interactions, expected_additional_interactions)
    assert equivalent(accredited_system_device, expected_device)


def test_process_request_to_add_device_product_team_exists(
    accredited_system: dict,
    repository: dict[str, Repository],
    input_questionnaires: dict,
    initial_product_team: ProductTeam,
    expected_product,
    expected_empty_message_sets,
    expected_additional_interactions,
    expected_device,
):
    repository["product_team_repository"].write(initial_product_team)
    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=accredited_system, **repository, **input_questionnaires
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)

    (product_created_event, product_key_added_event) = product.events
    (mhs_device_ref_data_created_event,) = message_sets.events
    (
        accredited_system_device_ref_data_created_event,
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        accredited_system_device_ref_data_questionnaire_updated_event_2,
    ) = additional_interactions.events
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events
    assert product_team.events == []
    assert isinstance(product_created_event, CpmProductCreatedEvent)
    assert isinstance(product_key_added_event, CpmProductKeyAddedEvent)
    assert isinstance(
        mhs_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_2,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )
    assert product_team == initial_product_team
    assert equivalent(product, expected_product)
    assert equivalent(message_sets, expected_empty_message_sets)
    assert equivalent(additional_interactions, expected_additional_interactions)
    assert equivalent(accredited_system_device, expected_device)


def test_process_request_to_add_device_product_exists(
    accredited_system: dict,
    repository: dict[str, Repository],
    input_questionnaires: dict,
    initial_product_team: ProductTeam,
    initial_product: CpmProduct,
    expected_empty_message_sets,
    expected_additional_interactions,
    expected_device,
):
    repository["product_team_repository"].write(initial_product_team)
    repository["product_repository"].write(initial_product)

    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=accredited_system, **repository, **input_questionnaires
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)
    assert product_team.events == []
    assert product.events == []

    (mhs_device_ref_data_created_event,) = message_sets.events
    (
        accredited_system_device_ref_data_created_event,
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        accredited_system_device_ref_data_questionnaire_updated_event_2,
    ) = additional_interactions.events
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events
    assert isinstance(
        mhs_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_2,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )
    assert product_team == initial_product_team
    assert product == initial_product
    assert equivalent(message_sets, expected_empty_message_sets)
    assert equivalent(additional_interactions, expected_additional_interactions)
    assert equivalent(accredited_system_device, expected_device)


def test_process_request_to_add_device_message_set_exists(
    accredited_system: dict,
    repository: dict[str, Repository],
    input_questionnaires: dict,
    initial_product_team: ProductTeam,
    initial_product: CpmProduct,
    non_empty_message_sets: DeviceReferenceData,
    expected_additional_interactions,
    expected_device,
):
    repository["product_team_repository"].write(initial_product_team)
    repository["product_repository"].write(initial_product)
    repository["device_reference_data_repository"].write(non_empty_message_sets)

    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=accredited_system, **repository, **input_questionnaires
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)
    assert product_team.events == []
    assert product.events == []
    assert message_sets.events == []

    (
        accredited_system_device_ref_data_created_event,
        accredited_system_device_ref_data_questionnaire_updated_event_1,
    ) = additional_interactions.events
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events
    assert isinstance(
        accredited_system_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )
    assert product_team == initial_product_team
    assert product == initial_product
    assert message_sets == non_empty_message_sets
    assert equivalent(accredited_system_device, expected_device)


def test_process_request_to_add_device_additional_interactions_exists(
    accredited_system: dict,
    repository: dict[str, Repository],
    input_questionnaires: dict,
    initial_product_team: ProductTeam,
    initial_product: CpmProduct,
    expected_empty_message_sets: DeviceReferenceData,
    initial_additional_interactions: DeviceReferenceData,
    expected_device,
):
    repository["product_team_repository"].write(initial_product_team)
    repository["product_repository"].write(initial_product)
    repository["device_reference_data_repository"].write(
        initial_additional_interactions
    )

    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=accredited_system, **repository, **input_questionnaires
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)
    assert product_team.events == []
    assert product.events == []

    (mhs_device_ref_data_created_event,) = message_sets.events
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events

    assert isinstance(
        mhs_device_ref_data_created_event, DeviceReferenceDataCreatedEvent
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )

    assert product_team == initial_product_team
    assert product == initial_product
    assert equivalent(message_sets, expected_empty_message_sets)
    assert equivalent(accredited_system_device, expected_device)


def test_process_request_to_add_as_device_exists(
    another_accredited_system: dict,
    repository: dict[str, Repository],
    input_questionnaires: dict,
    initial_product_team: ProductTeam,
    initial_product: CpmProduct,
    empty_message_sets: DeviceReferenceData,
    initial_additional_interactions: DeviceReferenceData,
    initial_accredited_system_device: Device,
    expected_additional_device,
):
    repository["product_team_repository"].write(initial_product_team)
    repository["product_repository"].write(initial_product)
    repository["device_reference_data_repository"].write(empty_message_sets)
    repository["device_reference_data_repository"].write(
        initial_additional_interactions
    )
    repository["device_repository"].write(initial_accredited_system_device)

    (
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ) = process_request_to_add_as(
        accredited_system=another_accredited_system,
        **input_questionnaires,
        **repository,
    )
    assert isinstance(product_team, ProductTeam)
    assert isinstance(product, CpmProduct)
    assert isinstance(message_sets, DeviceReferenceData)
    assert isinstance(additional_interactions, DeviceReferenceData)
    assert isinstance(accredited_system_device, Device)

    assert product_team.events == []
    assert product.events == []
    assert message_sets.events == []

    (accredited_system_device_ref_data_questionnaire_updated_event_1,) = (
        additional_interactions.events
    )
    (
        device_created_event,
        device_key_added_event,
        device_questionnaire_updated,
        device_tags_added_event,
        device_ref_data_added_event_message_sets,
        device_ref_data_added_event_additional_interactions,
    ) = accredited_system_device.events

    assert isinstance(
        accredited_system_device_ref_data_questionnaire_updated_event_1,
        DrdQuestionnaireUpdatedEvent,
    )
    assert isinstance(device_created_event, DeviceCreatedEvent)
    assert isinstance(device_questionnaire_updated, DeviceQuestionnaireUpdatedEvent)
    assert isinstance(device_key_added_event, DeviceKeyAddedEvent)
    assert isinstance(device_tags_added_event, DeviceTagsAddedEvent)
    assert isinstance(
        device_ref_data_added_event_message_sets, DeviceReferenceDataIdAddedEvent
    )
    assert isinstance(
        device_ref_data_added_event_additional_interactions,
        DeviceReferenceDataIdAddedEvent,
    )
    assert product_team == initial_product_team
    assert product == initial_product
    assert message_sets == empty_message_sets

    assert additional_interactions != initial_additional_interactions
    assert (
        additional_interactions.updated_on > initial_additional_interactions.updated_on
    )

    # Each as deviced should have 1 key each of it's corresponding ASID
    assert len(initial_accredited_system_device.keys) == 1
    assert len(accredited_system_device.keys) == 1
    assert equivalent(accredited_system_device, expected_additional_device)
