import pytest
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team_epr.v1 import ProductTeam
from domain.core.questionnaire.v1 import QuestionnaireResponse
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.epr_product_repository.v1 import EprProductRepository
from domain.repository.product_team_epr_repository.v1 import ProductTeamRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.epr.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.readers import (
    read_additional_interactions_if_exists,
    read_drds_from_as_device,
    read_message_sets_from_mhs_device,
    read_or_create_empty_message_sets,
    read_or_create_epr_product,
    read_or_create_epr_product_team,
    read_or_create_mhs_device,
)

from test_helpers.dynamodb import mock_table


@pytest.fixture
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture
def product(product_team):
    return create_epr_product(
        product_team=product_team, product_name="foo", party_key="AAA-111111"
    )


@pytest.fixture
def additional_interactions(product: EprProduct):
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=[],
    )


@pytest.fixture
def message_sets(product: EprProduct):
    return create_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        message_set_data=[],
    )


@pytest.fixture
def mhs_device_data():
    questionnaire = QuestionnaireRepository().read(name=QuestionnaireInstance.SPINE_MHS)
    raw_mhs_device_data = {
        "Address": "my-mhs-endpoint",
        "Approver URP": "approver-123",
        "DNS Approver": "dns-approver-123",
        "Date Approved": "today",
        "Date DNS Approved": "yesterday",
        "Date Requested": "a week ago",
        "MHS FQDN": "my-fqdn",
        "MHS Party Key": "AAA-123456",
        "Managing Organization": "AAA",
        "Product Name": "My EPR Product",
        "Requestor URP": "requester-123",
        "MHS Manufacturer Organisation": "AAA",
    }
    return questionnaire.validate(data=raw_mhs_device_data)


@pytest.fixture
def mhs_device(
    product: EprProduct,
    message_sets: DeviceReferenceData,
    mhs_device_data: QuestionnaireResponse,
):
    return create_mhs_device(
        cpa_ids=["er3243"],
        party_key=product.keys[0].key_value,
        product=product,
        message_sets_id=message_sets.id,
        mhs_device_data=mhs_device_data,
    )


@pytest.fixture
def as_device_data():
    questionnaire = QuestionnaireRepository().read(name=QuestionnaireInstance.SPINE_AS)
    raw_as_device_data = {
        "MHS Manufacturer Organisation": "AAA",
        "MHS Party Key": "AAA-123456",
        "ASID": "12345",
        "ODS Code": "AAA",
        "Client ODS Codes": ["BBB"],
        "Product Key": "6216",
        "Product Name": "My EPR Product",
        "Product Version": None,
        "Requestor URP": "requester-123",
        "Approver URP": "approver-123",
        "Date Approved": "today",
        "Date Requested": "a week ago",
        "Temp UID": None,
    }
    return questionnaire.validate(data=raw_as_device_data)


@pytest.fixture
def as_device(
    product: EprProduct,
    as_device_data: QuestionnaireResponse,
    additional_interactions: DeviceReferenceData,
    message_sets: DeviceReferenceData,
):
    return create_as_device(
        product=product,
        party_key=product.keys[0].key_value,
        asid="er3243",
        as_device_data=as_device_data,
        message_sets_id=message_sets.id,
        additional_interactions_id=additional_interactions.id,
        as_tags=[],
    )


@pytest.fixture
def db_client():
    with mock_table("foo") as client:
        yield client


@pytest.fixture
def product_team_repository(db_client):
    yield ProductTeamRepository(table_name="foo", dynamodb_client=db_client)


@pytest.fixture
def product_repository(db_client):
    yield EprProductRepository(table_name="foo", dynamodb_client=db_client)


@pytest.fixture
def device_reference_data_repository(db_client):
    yield DeviceReferenceDataRepository(table_name="foo", dynamodb_client=db_client)


@pytest.fixture
def device_repository(db_client):
    yield DeviceRepository(table_name="foo", dynamodb_client=db_client)


def test_read_or_create_epr_product_team(
    product_team: ProductTeam, product_team_repository: ProductTeamRepository
):
    product_team_repository.write(product_team)
    _product_team = read_or_create_epr_product_team(
        ods_code=product_team.ods_code, product_team_repository=product_team_repository
    )
    assert _product_team.state() == product_team.state()


def test_read_or_create_epr_product_team_default(
    product_team: ProductTeam, product_team_repository: ProductTeamRepository
):
    _product_team = read_or_create_epr_product_team(
        ods_code=product_team.ods_code, product_team_repository=product_team_repository
    )
    state = _product_team.state()
    expected_state = product_team.state()

    assert state.pop("created_on") > expected_state.pop("created_on")
    assert state.pop("id") != expected_state.pop("id")
    assert state == expected_state


def test_read_or_create_epr_product(
    product_team: ProductTeam,
    product: EprProduct,
    product_repository: EprProductRepository,
):
    product_repository.write(product)
    _product = read_or_create_epr_product(
        product_team=product_team,
        product_name=product.name,
        party_key=product.keys[0].key_value,
        product_repository=product_repository,
    )
    assert _product.state() == product.state()


def test_read_or_create_epr_product_default(
    product_team: ProductTeam,
    product: EprProduct,
    product_repository: EprProductRepository,
):
    _product = read_or_create_epr_product(
        product_team=product_team,
        product_name=product.name,
        party_key=product.keys[0].key_value,
        product_repository=product_repository,
    )
    state = _product.state()
    expected_state = product.state()

    assert state.pop("created_on") > expected_state.pop("created_on")
    assert state.pop("updated_on") > expected_state.pop("updated_on")
    assert state.pop("id") != expected_state.pop("id")
    assert state == expected_state


def test_read_additional_interactions_if_exists(
    additional_interactions: DeviceReferenceData,
    product: EprProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    device_reference_data_repository.write(additional_interactions)
    _additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product_team_id=product.product_team_id,
        product_id=product.id,
    )
    assert _additional_interactions == additional_interactions


def test_read_additional_interactions_if_exists_default(
    product: EprProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    _additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product_team_id=product.product_team_id,
        product_id=product.id,
    )
    assert _additional_interactions is None


def test_read_or_create_empty_message_sets(
    message_sets: DeviceReferenceData,
    product: EprProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    device_reference_data_repository.write(message_sets)
    _message_sets = read_or_create_empty_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        device_reference_data_repository=device_reference_data_repository,
    )
    assert message_sets == _message_sets


def test_read_or_create_empty_message_sets_default(
    message_sets: DeviceReferenceData,
    product: EprProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    _message_sets = read_or_create_empty_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        device_reference_data_repository=device_reference_data_repository,
    )

    state = _message_sets.state()
    expected_state = message_sets.state()

    assert state.pop("created_on") > expected_state.pop("created_on")
    assert state.pop("id") != expected_state.pop("id")
    assert state == expected_state


def test_read_or_update_mhs_device(
    product_team: ProductTeam,
    product: EprProduct,
    device_repository: DeviceRepository,
    message_sets: DeviceReferenceData,
    mhs_device: Device,
    mhs_device_data: QuestionnaireResponse,
):
    device_repository.write(mhs_device)

    _mhs_device = read_or_create_mhs_device(
        device_repository=device_repository,
        cpa_id=mhs_device.keys[0].key_value,
        party_key=product.keys[0].key_value,
        product_team=product_team,
        product=product,
        message_sets=message_sets,
        mhs_device_data=mhs_device_data,
    )

    assert _mhs_device == mhs_device


def test_create_or_update_mhs_device_default(
    product_team: ProductTeam,
    product: EprProduct,
    device_repository: DeviceRepository,
    message_sets: DeviceReferenceData,
    mhs_device: Device,
    mhs_device_data: QuestionnaireResponse,
):
    _mhs_device = read_or_create_mhs_device(
        device_repository=device_repository,
        cpa_id=mhs_device.keys[0].key_value,
        party_key=product.keys[0].key_value,
        product_team=product_team,
        product=product,
        message_sets=message_sets,
        mhs_device_data=mhs_device_data,
    )

    state_1 = mhs_device.state()
    state_2 = _mhs_device.state()
    assert state_1.pop("created_on") < state_2.pop("created_on")
    assert state_1.pop("updated_on") < state_2.pop("updated_on")
    assert state_1.pop("id") != state_2.pop("id")
    assert state_1 == state_2


def test_read_message_sets_from_mhs_device(
    mhs_device: Device,
    message_sets: DeviceReferenceData,
    device_repository: DeviceRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    device_repository.write(mhs_device)
    device_reference_data_repository.write(message_sets)

    message_sets_from_db = read_message_sets_from_mhs_device(
        mhs_device=mhs_device,
        device_reference_data_repository=device_reference_data_repository,
    )
    assert message_sets_from_db == message_sets


def test_read_drds_from_as_device(
    as_device: Device,
    additional_interactions: DeviceReferenceData,
    message_sets: DeviceReferenceData,
    device_repository: DeviceRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    device_repository.write(as_device)
    device_reference_data_repository.write(additional_interactions)
    device_reference_data_repository.write(message_sets)

    message_sets_from_db, additional_interactions_from_db = read_drds_from_as_device(
        as_device=as_device,
        device_reference_data_repository=device_reference_data_repository,
    )
    assert message_sets_from_db == message_sets
    assert additional_interactions_from_db == additional_interactions
