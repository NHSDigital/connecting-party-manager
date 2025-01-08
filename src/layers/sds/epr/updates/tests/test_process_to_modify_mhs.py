from copy import deepcopy

import pytest
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.error import ImmutableFieldError
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.bulk_create.tests.conftest import mhs_1  # noqa
from sds.epr.constants import SdsFieldName
from sds.epr.creators import (
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.getters import get_message_set_data, get_mhs_device_data
from sds.epr.updaters import UnexpectedModification
from sds.epr.updates.change_request_processors import (
    process_request_to_add_to_mhs,
    process_request_to_delete_from_mhs,
    process_request_to_replace_in_mhs,
)

from test_helpers.dynamodb import mock_table

CPA_ID_TO_MODIFY = "123"
MESSAGE_SET_FIELD_TO_ADD_TO = "nhs_mhs_is_authenticated"
MESSAGE_SET_FIELD_TO_DELETE = "nhs_contract_property_template_key"
DEVICE_FIELD_TO_ADD_TO = "nhs_product_version"
DEVICE_FIELD_TO_DELETE = "nhs_product_name"


@pytest.fixture
def mhs(mhs_1: NhsMhs):
    """Alias to fixture from sds.epr.bulk_create.tests.conftest"""
    # Nullify a couple of variables we want to test adding back in
    setattr(mhs_1, MESSAGE_SET_FIELD_TO_ADD_TO, None)
    setattr(mhs_1, DEVICE_FIELD_TO_ADD_TO, None)
    return mhs_1.dict()


@pytest.fixture
def another_mhs(mhs):
    mhs = deepcopy(mhs)
    mhs["nhs_mhs_svc_ia"] = "another-interaction-id"
    mhs["nhs_mhs_cpa_id"] = CPA_ID_TO_MODIFY
    return mhs


@pytest.fixture
def product_team(mhs_1: NhsMhs):
    return create_epr_product_team(ods_code=mhs_1.nhs_mhs_manufacturer_org)


@pytest.fixture
def product(mhs_1: NhsMhs, product_team):
    return create_epr_product(
        product_team=product_team,
        product_name=mhs_1.nhs_product_name,
        party_key=mhs_1.nhs_mhs_party_key,
    )


@pytest.fixture
def message_sets(mhs: dict, another_mhs: dict, mhs_1: NhsMhs, product):
    message_set_data = get_message_set_data(
        message_handling_systems=[mhs, another_mhs],
        message_set_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
        message_set_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
    )
    return create_message_sets(
        product=product,
        party_key=mhs_1.nhs_mhs_party_key,
        message_set_data=message_set_data,
    )


@pytest.fixture
def mhs_device(
    mhs: dict,
    mhs_1: NhsMhs,
    product,
    message_sets: DeviceReferenceData,
):
    mhs_device_data = get_mhs_device_data(
        mhs=mhs,
        mhs_device_questionnaire=QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS
        ),
        mhs_device_field_mapping=QuestionnaireRepository().read_field_mapping(
            QuestionnaireInstance.SPINE_MHS
        ),
    )

    return create_mhs_device(
        product=product,
        party_key=mhs_1.nhs_mhs_party_key,
        mhs_device_data=mhs_device_data,
        cpa_ids=[mhs_1.nhs_mhs_cpa_id, CPA_ID_TO_MODIFY],
        message_sets_id=message_sets.id,
    )


@pytest.fixture
def device_reference_data_repository():
    with mock_table("foo") as client:
        yield DeviceReferenceDataRepository(table_name="foo", dynamodb_client=client)


@pytest.fixture
def common_kwargs(device_reference_data_repository):
    questionnaire_repository = QuestionnaireRepository()
    return dict(
        cpa_id_to_modify=CPA_ID_TO_MODIFY,
        device_reference_data_repository=device_reference_data_repository,
        mhs_device_questionnaire=questionnaire_repository.read(
            QuestionnaireInstance.SPINE_MHS
        ),
        mhs_device_field_mapping=questionnaire_repository.read_field_mapping(
            QuestionnaireInstance.SPINE_MHS
        ),
        message_set_questionnaire=questionnaire_repository.read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
        message_set_field_mapping=questionnaire_repository.read_field_mapping(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        ),
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "nhs_mhs_manufacturer_org",
        "nhs_mhs_party_key",
        "nhs_mhs_cpa_id",
        "unique_identifier",
    ],
)
def test_process_request_to_add_to_mhs__immutable_fields(field_name, common_kwargs):
    with pytest.raises(ImmutableFieldError):
        process_request_to_add_to_mhs(
            field_name=field_name, device=None, new_values=None, **common_kwargs
        )


def message_sets_correctly_updated(
    initial_message_sets: dict,
    final_message_sets: dict,
    field_name: str,
    new_value: str,
    check_value=True,
):
    assert final_message_sets["id"] == initial_message_sets["id"]
    assert final_message_sets["created_on"] == initial_message_sets["created_on"]

    # Responses should be same length
    initial_responses = initial_message_sets["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}/1"
    ]
    final_responses = final_message_sets["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}/1"
    ]
    assert len(final_responses) == len(initial_responses)

    initial_responses_data = [message_set["data"] for message_set in initial_responses]
    final_responses_data = [message_set["data"] for message_set in final_responses]

    # One message set should have been removed
    (message_set_that_has_been_removed,) = (
        message_set
        for message_set in initial_responses_data
        if message_set not in final_responses_data
    )
    assert message_set_that_has_been_removed[SdsFieldName.CPA_ID] == CPA_ID_TO_MODIFY

    # One message set should have been added with the updated value
    (message_set_that_has_been_added,) = (
        message_set
        for message_set in final_responses_data
        if message_set not in initial_responses_data
    )
    assert message_set_that_has_been_added[SdsFieldName.CPA_ID] == CPA_ID_TO_MODIFY

    if check_value:
        assert message_set_that_has_been_added[field_name] == new_value
    return True


def mhs_device_correctly_updated(
    initial_device: dict,
    final_device: dict,
    field_name: str,
    new_value: str,
    check_value=True,
    value_was_replaced=False,
):
    assert final_device["id"] == initial_device["id"]
    assert final_device["created_on"] == initial_device["created_on"]

    # Responses should be same length
    initial_responses = initial_device["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_MHS}/1"
    ]
    final_responses = final_device["questionnaire_responses"][
        f"{QuestionnaireInstance.SPINE_MHS}/1"
    ]
    assert len(final_responses) == len(initial_responses)

    (initial_responses_data,) = (
        message_set["data"] for message_set in initial_responses
    )
    (final_responses_data,) = (message_set["data"] for message_set in final_responses)

    if not value_was_replaced:
        assert field_name not in initial_responses_data
        final_value = final_responses_data.pop(field_name)
        if check_value:
            assert final_value == new_value
    else:
        assert field_name in initial_responses_data
        final_value = final_responses_data.pop(field_name)
        initial_value = initial_responses_data.pop(field_name)
        assert final_value != initial_value
        assert final_value == new_value

    assert initial_responses_data == final_responses_data
    return True


def test_process_request_to_add_to_mhs__message_set_add_to_empty_non_list_field_with_single_value_replaces_value(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    message_set_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = MESSAGE_SET_FIELD_TO_ADD_TO
    _field_to_modify = message_set_field_mapping[field_to_modify]
    new_value = "none"

    _device, _message_sets = process_request_to_add_to_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only message set was modified
    assert initial_device == final_device
    assert message_sets_correctly_updated(
        initial_message_sets=initial_message_sets,
        final_message_sets=final_message_sets,
        field_name=_field_to_modify,
        new_value=new_value,
    )
    assert final_message_sets["updated_on"] > initial_message_sets["updated_on"]


def test_process_request_to_add_to_mhs__message_set_add_to_existing_non_list_field_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_mhs(
            device=mhs_device,
            field_name="nhs_mhs_in",
            new_values=["a new value"],
            **common_kwargs,
        )


def test_process_request_to_add_to_mhs__message_set_add_to_empty_non_list_field_with_multiple_values_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_mhs(
            device=mhs_device,
            field_name="nhs_mhs_actor",
            new_values=["urn:oasis:names:tc:ebxml-msg:actor:topartymsh", "ignored"],
            **common_kwargs,
        )


def test_process_request_to_add_to_mhs__device_add_to_empty_non_list_field_with_single_value_replaces_value(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    mhs_device_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = DEVICE_FIELD_TO_ADD_TO
    _field_to_modify = mhs_device_field_mapping[field_to_modify]
    new_value = "2001.01"

    _device, _message_sets = process_request_to_add_to_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only device was modified
    assert initial_message_sets == final_message_sets
    assert mhs_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_value=new_value,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_add_to_mhs__device_add_to_existing_non_list_field_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_mhs(
            device=mhs_device,
            field_name="nhs_requestor_urp",
            new_values=["another-urp"],
            **common_kwargs,
        )


def test_process_request_to_add_to_mhs__device_add_to_empty_non_list_field_with_multiple_values_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_add_to_mhs(
            device=mhs_device,
            field_name=DEVICE_FIELD_TO_ADD_TO,
            new_values=["next-week", "today"],
            **common_kwargs,
        )


def test_process_request_to_delete_from_mhs__device(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    message_set_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = DEVICE_FIELD_TO_DELETE
    _field_to_modify = message_set_field_mapping[field_to_modify]

    _device, _message_sets = process_request_to_delete_from_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only device was modified
    assert initial_message_sets == final_message_sets
    # Run this function "in reverse" as a delete is the opposite of an add
    assert mhs_device_correctly_updated(
        initial_device=final_device,
        final_device=initial_device,
        field_name=_field_to_modify,
        new_value=None,
        check_value=False,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_delete_from_mhs__device_required_field_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_delete_from_mhs(
            device=mhs_device,
            field_name="nhs_mhs_fqdn",
            new_values=[],
            **common_kwargs,
        )


def test_process_request_to_delete_from_mhs__message_sets(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    message_set_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = MESSAGE_SET_FIELD_TO_DELETE
    _field_to_modify = message_set_field_mapping[field_to_modify]

    _device, _message_sets = process_request_to_delete_from_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only message set was modified
    assert initial_device == final_device

    # Run this function "in reverse" as a delete is the opposite of an add
    assert message_sets_correctly_updated(
        initial_message_sets=final_message_sets,
        final_message_sets=initial_message_sets,
        field_name=_field_to_modify,
        new_value=None,
        check_value=False,
    )
    assert final_message_sets["updated_on"] > initial_message_sets["updated_on"]


def test_process_request_to_delete_from_mhs__message_set_required_field_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_delete_from_mhs(
            device=mhs_device,
            field_name="nhs_mhs_sn",
            new_values=[],
            **common_kwargs,
        )


def test_process_request_to_replace_in_mhs__message_set_replace_in_existing_non_list_field_sets_value(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    message_sets_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = "nhs_mhs_in"
    _field_to_modify = message_sets_field_mapping[field_to_modify]
    new_value = "a new value"

    _device, _message_sets, additional_interactions = process_request_to_replace_in_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only device was modified
    assert initial_device == final_device
    assert message_sets_correctly_updated(
        initial_message_sets=initial_message_sets,
        final_message_sets=final_message_sets,
        field_name=_field_to_modify,
        new_value=new_value,
    )
    assert final_message_sets["updated_on"] > initial_message_sets["updated_on"]


def test_process_request_to_replace_in_mhs__message_set_replace_in_empty_non_list_field_with_multiple_values_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    with pytest.raises(UnexpectedModification):
        process_request_to_replace_in_mhs(
            device=mhs_device,
            field_name="nhs_mhs_actor",
            new_values=["urn:oasis:names:tc:ebxml-msg:actor:topartymsh", "ignored"],
            **common_kwargs,
        )


def test_process_request_to_replace_in_mhs__device_replace_in_empty_non_list_field_with_single_value_replaces_value(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    mhs_device_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = DEVICE_FIELD_TO_ADD_TO
    _field_to_modify = mhs_device_field_mapping[field_to_modify]
    new_value = "2001.01"

    _device, _message_sets, additional_interactions = process_request_to_replace_in_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only device was modified
    assert initial_message_sets == final_message_sets
    assert mhs_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_value=new_value,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_replace_in_mhs__device_replace_in_existing_non_list_field_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)

    mhs_device_field_mapping = QuestionnaireRepository().read_field_mapping(
        QuestionnaireInstance.SPINE_MHS
    )

    initial_device = mhs_device.state()
    initial_message_sets = message_sets.state()

    field_to_modify = "nhs_requestor_urp"
    _field_to_modify = mhs_device_field_mapping[field_to_modify]
    new_value = "another-urp"

    _device, _message_sets, additional_interactions = process_request_to_replace_in_mhs(
        device=mhs_device,
        field_name=field_to_modify,
        new_values=[new_value],
        **common_kwargs,
    )

    final_device = _device.state()
    final_message_sets = _message_sets.state()

    # Check only device was modified
    assert initial_message_sets == final_message_sets
    assert mhs_device_correctly_updated(
        initial_device=initial_device,
        final_device=final_device,
        field_name=_field_to_modify,
        new_value=new_value,
        value_was_replaced=True,
    )
    assert final_device["updated_on"] > initial_device["updated_on"]


def test_process_request_to_replace_in_mhs__device_replace_in_empty_non_list_field_with_multiple_values_raises_error(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_reference_data_repository: DeviceReferenceDataRepository,
    common_kwargs,
):
    device_reference_data_repository.write(message_sets)
    with pytest.raises(UnexpectedModification):
        process_request_to_replace_in_mhs(
            device=mhs_device,
            field_name=DEVICE_FIELD_TO_ADD_TO,
            new_values=["next-week", "today"],
            **common_kwargs,
        )
