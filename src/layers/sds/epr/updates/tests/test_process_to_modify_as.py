import pytest
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.error import ImmutableFieldError
from domain.questionnaire_instances.constants import QuestionnaireInstance
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.bulk_create.tests.conftest import accredited_system_1  # noqa
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
)
from sds.epr.updaters import UnexpectedModification
from sds.epr.updates.change_request_processors import (
    process_request_to_add_to_as,
    process_request_to_delete_from_as,
)

from test_helpers.dynamodb import mock_table

ASID_TO_MODIFY = "123"
ADDITIONAL_INTERACTIONS_FIELD_TO_ADD_TO = "nhs_as_svc_ia"
DEVICE_FIELD_TO_ADD_TO = "description"
DEVICE_LIST_FIELD_TO_ADD_TO = "nhs_as_client"
DEVICE_FIELD_TO_DELETE = "nhs_as_category_bag"


@pytest.fixture
def accredited_system(accredited_system_1: NhsMhs):
    """Alias to fixture from sds.epr.bulk_create.tests.conftest"""
    return accredited_system_1.dict()


@pytest.fixture
def product_team(accredited_system_1: NhsMhs):
    return create_epr_product_team(
        ods_code=accredited_system_1.nhs_mhs_manufacturer_org
    )


@pytest.fixture
def product(accredited_system_1: NhsMhs, product_team):
    return create_epr_product(
        product_team=product_team,
        product_name=accredited_system_1.nhs_product_name,
        party_key=accredited_system_1.nhs_mhs_party_key,
    )


@pytest.fixture
def empty_message_sets(accredited_system_1: NhsMhs, product):
    return create_message_sets(
        product=product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        message_set_data=[],
    )


@pytest.fixture
def additional_interactions(accredited_system_1: NhsAccreditedSystem, product):
    additional_interactions_data = get_additional_interactions_data(
        accredited_systems=[accredited_system_1.dict()],
        additional_interactions_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
    )
    return create_additional_interactions(
        product=product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        additional_interactions_data=additional_interactions_data,
    )


@pytest.fixture
def accredited_system_device(
    accredited_system: dict,
    accredited_system_1: NhsMhs,
    product,
    additional_interactions: DeviceReferenceData,
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
        product=product,
        party_key=accredited_system_1.nhs_mhs_party_key,
        asid=accredited_system_1.unique_identifier,
        as_device_data=accredited_system_device_data,
        message_sets_id=empty_message_sets.id,
        additional_interactions_id=additional_interactions.id,
        as_tags=as_tags,
    )


@pytest.fixture
def db_client():
    with mock_table("foo") as client:
        yield client


@pytest.fixture
def device_reference_data_repository(db_client):
    yield DeviceReferenceDataRepository(table_name="foo", dynamodb_client=db_client)


@pytest.fixture
def device_repository(db_client):
    yield DeviceRepository(table_name="foo", dynamodb_client=db_client)


@pytest.fixture
def common_kwargs(device_reference_data_repository, device_repository):
    questionnaire_repository = QuestionnaireRepository()
    return dict(
        device_repository=device_repository,
        device_reference_data_repository=device_reference_data_repository,
        accredited_system_questionnaire=questionnaire_repository.read(
            QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=questionnaire_repository.read_field_mapping(
            QuestionnaireInstance.SPINE_AS
        ),
        additional_interactions_questionnaire=questionnaire_repository.read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
        additional_interactions_field_mapping=questionnaire_repository.read_field_mapping(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "nhs_mhs_manufacturer_org",
        "nhs_mhs_party_key",
        "unique_identifier",
    ],
)
def test_process_request_to_modify_as__immutable_fields(field_name, common_kwargs):
    with pytest.raises(ImmutableFieldError):
        process_request_to_add_to_as(
            field_name=field_name,
            device=None,
            new_values=["new_value"],
            **common_kwargs,
        )
    with pytest.raises(ImmutableFieldError):
        process_request_to_delete_from_as(
            field_name=field_name, device=None, new_values=None, **common_kwargs
        )


def additional_interactions_correctly_updated(
    initial_additional_interactions: dict,
    final_additional_interactions: dict,
    field_name: str,
    new_values: set[str],
):
    assert final_additional_interactions["id"] == initial_additional_interactions["id"]
    assert (
        final_additional_interactions["created_on"]
        == initial_additional_interactions["created_on"]
    )

    # There should be one extra additional interactions response
    initial_responses = initial_additional_interactions["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS}/1"
    ]
    final_responses = final_additional_interactions["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS}/1"
    ]
    assert len(final_responses) == len(initial_responses) + 1

    initial_responses_data = [
        additional_interactions["data"] for additional_interactions in initial_responses
    ]
    final_responses_data = [
        additional_interactions["data"] for additional_interactions in final_responses
    ]

    # Additional interactions should have been added
    additional_interactions_that_have_been_added = (
        additional_interaction
        for additional_interaction in final_responses_data
        if additional_interaction not in initial_responses_data
    )
    for additional_interaction in additional_interactions_that_have_been_added:
        assert additional_interaction[field_name] in new_values

    return True


def as_device_correctly_updated(
    initial_device: dict,
    final_device: dict,
    field_name: str,
    new_values: set | list | None,
    check_value=True,
    value_was_replaced=False,
):
    assert final_device["id"] == initial_device["id"]
    assert final_device["created_on"] == initial_device["created_on"]

    # Responses should be same length
    initial_responses = initial_device["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_AS}/1"
    ]
    final_responses = final_device["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_AS}/1"
    ]
    assert len(final_responses) == len(initial_responses)

    (initial_responses_data,) = (
        additional_interactions["data"] for additional_interactions in initial_responses
    )
    (final_responses_data,) = (
        additional_interactions["data"] for additional_interactions in final_responses
    )

    # If value was not replaced
    if not value_was_replaced:
        assert (
            field_name not in initial_responses_data
            or initial_responses_data[field_name] is None
            or (
                isinstance(initial_responses_data[field_name], list)
                and (new_values is None or isinstance(new_values, list))
            )
        )
        final_value = final_responses_data.pop(field_name, None)
        if check_value:
            if new_values is None:
                assert final_value is None  # Ensure the value has been deleted
            elif isinstance(final_value, list):
                assert all(new_value in final_value for new_value in new_values)
            else:
                assert final_value == new_values
    else:
        # If value was replaced
        assert field_name in initial_responses_data
        final_value = final_responses_data.pop(field_name, None)
        initial_value = initial_responses_data.pop(field_name)
        assert final_value != initial_value
        if new_values is None:
            assert final_value is None  # Ensure the value was removed
        elif isinstance(final_value, list):
            assert all(new_value in final_value for new_value in new_values)
        else:
            assert final_value == new_values

    # Remaining data must match, excluding the field that was changed
    # This ensures only the targeted field differs
    for key in initial_responses_data.keys() - {field_name}:
        assert initial_responses_data[key] == final_responses_data.get(key)

    return True


def test_process_request_to_add_to_as__additional_interactions_add_to_field(
    accredited_system_device: Device,
    device_repository: DeviceRepository,
    empty_message_sets: DeviceReferenceData,
    additional_interactions: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_repository.write(accredited_system_device)
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)

    additional_interactions_field_mapping = (
        QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
    )

    initial_device = accredited_system_device.state()
    initial_additional_interactions = additional_interactions.state()

    field_to_modify = ADDITIONAL_INTERACTIONS_FIELD_TO_ADD_TO
    _field_to_modify = additional_interactions_field_mapping[field_to_modify]

    new_value = "another-interaction-id"

    _device, _additional_interactions = process_request_to_add_to_as(
        device=accredited_system_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_additional_interactions = _additional_interactions.state()

    # Check additional interactions was modified
    assert additional_interactions_correctly_updated(
        initial_additional_interactions=initial_additional_interactions,
        final_additional_interactions=final_additional_interactions,
        field_name=_field_to_modify,
        new_values=[new_value],
    )
    # Tags added for new interaction id
    assert len(final_device["tags"]) == len(initial_device["tags"]) + 2
    assert (
        final_additional_interactions["updated_on"]
        > initial_additional_interactions["updated_on"]
    )


def test_process_request_to_add_to_as__device_add_to_empty_non_list_field_with_single_value_replaces_value(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)

    accredited_system_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    )

    initial_device = accredited_system_device.state()
    initial_additional_interactions = additional_interactions.state()

    field_to_modify = DEVICE_FIELD_TO_ADD_TO
    _field_to_modify = accredited_system_field_mapping[field_to_modify]
    new_value = "description..."

    _device, _additional_interactions = process_request_to_add_to_as(
        device=accredited_system_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_additional_interactions = _additional_interactions.state()

    # Check only device was modified
    assert initial_additional_interactions == final_additional_interactions
    assert as_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_values=(new_value),
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_add_to_as__device_add_to_list_field(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)

    accredited_system_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    )

    initial_device = accredited_system_device.state()
    initial_additional_interactions = additional_interactions.state()

    field_to_modify = DEVICE_LIST_FIELD_TO_ADD_TO
    _field_to_modify = accredited_system_field_mapping[field_to_modify]
    new_values = ["nhs_as_client_2", "nhs_as_client_3"]

    _device, _additional_interactions = process_request_to_add_to_as(
        device=accredited_system_device,
        field_name=field_to_modify,
        new_values=new_values,
        **common_kwargs,
    )

    final_device = _device.state()
    final_additional_interactions = _additional_interactions.state()

    # Check only device was modified
    assert initial_additional_interactions == final_additional_interactions
    assert as_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_values=new_values,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_add_to_as__device_add_to_existing_non_list_field_raises_error(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)
    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_as(
            device=accredited_system_device,
            field_name="nhs_requestor_urp",
            new_values=["another-urp"],
            **common_kwargs,
        )


def test_process_request_to_add_to_as__device_add_to_empty_non_list_field_with_multiple_values_raises_error(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)
    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_as(
            device=accredited_system_device,
            field_name=DEVICE_FIELD_TO_ADD_TO,
            new_values=["next-week", "today"],
            **common_kwargs,
        )


def test_process_request_to_delete_from_as__device(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)

    accredited_system_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_AS
    )

    initial_device = accredited_system_device.state()
    initial_additional_interactions = additional_interactions.state()

    field_to_modify = DEVICE_FIELD_TO_DELETE
    _field_to_modify = accredited_system_field_mapping[field_to_modify]

    _device, _additional_interactions = process_request_to_delete_from_as(
        device=accredited_system_device,
        field_name=field_to_modify,
        new_values=[],
        **common_kwargs,
    )

    final_device = _device.state()
    final_additional_interactions = _additional_interactions.state()

    # Check only device was modified
    assert initial_additional_interactions == final_additional_interactions
    assert as_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_values=None,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_delete_from_as__additional_interactions_required_field_raises_error(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)
    with pytest.raises(UnexpectedModification):
        process_request_to_delete_from_as(
            device=accredited_system_device,
            field_name="nhs_as_svc_ia",
            new_values=None,
            **common_kwargs,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "nhs_id_code",
        "nhs_as_client",
        "nhs_product_key",
        "nhs_product_name",
        "nhs_product_version",
        "nhs_requestor_urp",
        "nhs_approver_urp",
        "nhs_date_approved",
        "nhs_date_requested",
        "nhs_temp_uid",
    ],
)
def test_process_request_to_delete_from_as__device_required_field_raises_error(
    accredited_system_device: Device,
    additional_interactions: DeviceReferenceData,
    empty_message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
    field_name,
):
    device_reference_data_repository.write(empty_message_sets)
    device_reference_data_repository.write(additional_interactions)
    with pytest.raises(UnexpectedModification):
        process_request_to_delete_from_as(
            device=accredited_system_device,
            field_name=field_name,
            new_values=None,
            **common_kwargs,
        )
