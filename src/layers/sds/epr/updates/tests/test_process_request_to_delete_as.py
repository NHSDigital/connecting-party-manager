import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    QuestionnaireResponseUpdatedEvent,
)
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
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.epr.bulk_create.tests.conftest import accredited_system_1  # noqa
from sds.epr.bulk_create.tests.conftest import accredited_system_2  # noqa
from sds.epr.creators import create_additional_interactions, create_as_device
from sds.epr.getters import (
    get_accredited_system_device_data,
    get_additional_interactions_data,
)
from sds.epr.updates.change_request_processors import process_request_to_delete_as
from sds.epr.updates.etl_device import DeviceHardDeletedEvent

from test_helpers.dynamodb import mock_table


@pytest.fixture
def product_team():
    ods_org = Root.create_ods_organisation(ods_code="AAA")
    return ods_org.create_product_team(name="my product team")


@pytest.fixture
def product(product_team: ProductTeam):
    return product_team.create_cpm_product(name="my product")


@pytest.fixture
def additional_interactions_data(
    accredited_system_1: NhsAccreditedSystem, accredited_system_2: NhsAccreditedSystem
):
    return get_additional_interactions_data(
        accredited_systems=[accredited_system_1.dict(), accredited_system_2.dict()],
        additional_interactions_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        ),
    )


@pytest.fixture
def as_device_1(
    accredited_system_1: NhsAccreditedSystem,
    additional_interactions: DeviceReferenceData,
    product: CpmProduct,
):
    as_device_data = get_accredited_system_device_data(
        accredited_system=accredited_system_1.dict(),
        accredited_system_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_AS
        ),
    )
    return create_as_device(
        product=product,
        party_key="123",
        asid="123456",
        as_device_data=as_device_data,
        message_sets_id="123",
        additional_interactions_id=additional_interactions.id,
        as_tags=[{"foo": "bar", "bar": "foo"}, {"foo": "bar"}],
    )


@pytest.fixture
def as_device_2(
    accredited_system_2: NhsAccreditedSystem,
    additional_interactions: DeviceReferenceData,
    product: CpmProduct,
):
    as_device_data = get_accredited_system_device_data(
        accredited_system=accredited_system_2.dict(),
        accredited_system_questionnaire=QuestionnaireRepository().read(
            name=QuestionnaireInstance.SPINE_AS
        ),
        accredited_system_field_mapping=QuestionnaireRepository().read_field_mapping(
            name=QuestionnaireInstance.SPINE_AS
        ),
    )
    return create_as_device(
        product=product,
        party_key="123",
        asid="345678",
        as_device_data=as_device_data,
        message_sets_id="123",
        additional_interactions_id=additional_interactions.id,
        as_tags=[{"foo": "bar", "bar": "foo"}, {"foo": "bar"}],
    )


@pytest.fixture
def additional_interactions(product: CpmProduct, additional_interactions_data):
    return create_additional_interactions(
        product=product,
        party_key="123",
        additional_interactions_data=additional_interactions_data,
    )


def test_process_request_to_delete_as__there_are_other_as_devices_so_dont_clear_as_drd(
    as_device_1: Device,
    as_device_2: Device,
    additional_interactions: DeviceReferenceData,
):
    table_name = "my-table"
    with mock_table(table_name=table_name) as client:
        device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=table_name, dynamodb_client=client
        )

        device_repo.write(as_device_1)
        device_repo.write(as_device_2)
        device_reference_data_repo.write(additional_interactions)

        device_to_delete = device_repo.read(
            product_team_id=as_device_1.product_team_id,
            product_id=as_device_1.product_id,
            id=as_device_1.id,
        )
        etl_device, modified_additional_interactions = process_request_to_delete_as(
            device=device_to_delete,
            device_repository=device_repo,
            device_reference_data_repository=device_reference_data_repo,
        )

    assert etl_device.events == [
        DeviceHardDeletedEvent(
            id=str(as_device_1.id),
            keys=[k.dict() for k in as_device_1.keys],
            tags=sorted(t.value for t in as_device_1.tags),
        )
    ]

    assert modified_additional_interactions == additional_interactions
    assert modified_additional_interactions.events == []


def test_process_request_to_delete_as__there_are_no_more_as_devices_so_do_clear_as_drd(
    as_device_1: Device,
    additional_interactions: DeviceReferenceData,
):
    table_name = "my-table"
    with mock_table(table_name=table_name) as client:
        device_repo = DeviceRepository(table_name=table_name, dynamodb_client=client)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=table_name, dynamodb_client=client
        )
        device_repo.write(as_device_1)
        device_reference_data_repo.write(additional_interactions)

        device_to_delete = device_repo.read(
            product_team_id=as_device_1.product_team_id,
            product_id=as_device_1.product_id,
            id=as_device_1.id,
        )
        etl_device, modified_additional_interactions = process_request_to_delete_as(
            device=device_to_delete,
            device_repository=device_repo,
            device_reference_data_repository=device_reference_data_repo,
        )

    assert etl_device.events == [
        DeviceHardDeletedEvent(
            id=str(as_device_1.id),
            keys=[k.dict() for k in as_device_1.keys],
            tags=sorted(t.value for t in as_device_1.tags),
        )
    ]

    qid = f"{QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS}/1"
    assert modified_additional_interactions.questionnaire_responses[qid] == []

    additional_interactions.questionnaire_responses[qid] = []
    modified_additional_interactions_state = modified_additional_interactions.state()
    additional_interactions_state = additional_interactions.state()

    assert modified_additional_interactions_state.pop(
        "updated_on"
    ) > additional_interactions_state.pop("updated_on")
    assert modified_additional_interactions_state == additional_interactions_state

    (event,) = modified_additional_interactions.events
    assert event == QuestionnaireResponseUpdatedEvent(
        id=str(additional_interactions.id),
        questionnaire_responses={qid: []},
        updated_on=event.updated_on,
    )
