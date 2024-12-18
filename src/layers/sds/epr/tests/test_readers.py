import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire.v1 import QuestionnaireResponse
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
from sds.epr.creators import (
    create_additional_interactions,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.readers import (
    read_additional_interactions_if_exists,
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
def additional_interactions(product: CpmProduct):
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=[],
    )


@pytest.fixture
def message_sets(product: CpmProduct):
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
    product: CpmProduct,
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
def product_team_repository():
    with mock_table("foo") as client:
        yield ProductTeamRepository(table_name="foo", dynamodb_client=client)


@pytest.fixture
def product_repository():
    with mock_table("foo") as client:
        yield CpmProductRepository(table_name="foo", dynamodb_client=client)


@pytest.fixture
def device_reference_data_repository():
    with mock_table("foo") as client:
        yield DeviceReferenceDataRepository(table_name="foo", dynamodb_client=client)


@pytest.fixture
def device_repository():
    with mock_table("foo") as client:
        yield DeviceRepository(table_name="foo", dynamodb_client=client)


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
    product: CpmProduct,
    product_repository: CpmProductRepository,
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
    product: CpmProduct,
    product_repository: CpmProductRepository,
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
    product: CpmProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    device_reference_data_repository.write(additional_interactions)
    _additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product=product,
    )
    assert _additional_interactions == additional_interactions


def test_read_additional_interactions_if_exists_default(
    product: CpmProduct,
    device_reference_data_repository: DeviceReferenceDataRepository,
):
    _additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product=product,
    )
    assert _additional_interactions is None


def test_read_or_create_empty_message_sets(
    message_sets: DeviceReferenceData,
    product: CpmProduct,
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
    product: CpmProduct,
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
    product: CpmProduct,
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
    product: CpmProduct,
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
