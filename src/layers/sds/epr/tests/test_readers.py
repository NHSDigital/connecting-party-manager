from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_repository.v1 import ProductTeamRepository
import pytest
from sds.epr.creators import (
    create_additional_interactions,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
)
from sds.epr.readers import (
    read_additional_interactions_if_exists,
    read_or_create_empty_message_sets,
    read_or_create_epr_product,
    read_or_create_epr_product_team,
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
