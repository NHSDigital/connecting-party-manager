import pytest
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.enum import Environment
from domain.core.product_key.v1 import ProductKeyType
from domain.core.product_team.v1 import ProductTeam
from domain.core.product_team_key.v1 import ProductTeamKey, ProductTeamKeyType
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from sds.epr.bulk_create.bulk_repository import (
    BulkRepository,
    exponential_backoff_with_jitter,
    retry_with_jitter,
)

from test_helpers.dynamodb import mock_table

TABLE_NAME = "my-table"


def test_exponential_backoff_with_jitter():
    base_delay = 0.1
    max_delay = 5
    min_delay = 0.05
    n_samples = 1000

    delays = []
    for retry in range(n_samples):
        delay = exponential_backoff_with_jitter(
            n_retries=retry,
            base_delay=base_delay,
            min_delay=min_delay,
            max_delay=max_delay,
        )
        assert max_delay >= delay >= min_delay
        delays.append(delay)
    assert len(set(delays)) == n_samples  # all delays should be unique
    assert sum(delays[n_samples:]) < sum(
        delays[:n_samples]
    )  # final delays should be larger than first delays


@pytest.mark.parametrize(
    "error_code",
    [
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
        "InternalServerError",
    ],
)
def test_retry_with_jitter_all_fail(error_code: str):
    class MockException(Exception):
        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    max_retries = 3

    @retry_with_jitter(max_retries=max_retries, error=MockException)
    def throw(error_code):
        raise MockException(error_code=error_code)

    with pytest.raises(ExceptionGroup) as exception_info:
        throw(error_code=error_code)

    assert (
        exception_info.value.message
        == f"Failed to put item after {max_retries} retries"
    )
    assert len(exception_info.value.exceptions) == max_retries
    assert all(
        isinstance(exc, MockException) for exc in exception_info.value.exceptions
    )


@pytest.mark.parametrize(
    "error_code",
    [
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
        "InternalServerError",
    ],
)
def test_retry_with_jitter_third_passes(error_code: str):
    class MockException(Exception):
        retries = 0

        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    max_retries = 3

    @retry_with_jitter(max_retries=max_retries, error=MockException)
    def throw(error_code):
        if MockException.retries == max_retries - 1:
            return "foo"
        MockException.retries += 1
        raise MockException(error_code=error_code)

    assert throw(error_code=error_code) == "foo"


@pytest.mark.parametrize(
    "error_code",
    [
        "SomeOtherError",
    ],
)
def test_retry_with_jitter_other_code(error_code: str):
    class MockException(Exception):
        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    @retry_with_jitter(max_retries=3, error=MockException)
    def throw(error_code):
        raise MockException(error_code=error_code)

    with pytest.raises(MockException) as exception_info:
        throw(error_code=error_code)

    assert exception_info.value.response == {"Error": {"Code": error_code}}


def test_retry_with_jitter_other_exception():
    @retry_with_jitter(max_retries=3, error=ValueError)
    def throw():
        raise TypeError()

    with pytest.raises(TypeError):
        throw()


@pytest.fixture
def dynamodb_client():
    with mock_table(TABLE_NAME) as client:
        yield client


def test_BulkRepository_handle_ProductTeam(dynamodb_client):
    product_team_repo = ProductTeamRepository(
        table_name=TABLE_NAME, dynamodb_client=dynamodb_client
    )
    product_team = ProductTeam(
        name="my-product",
        ods_code="AAA",
        keys=[ProductTeamKey(key_type=ProductTeamKeyType.EPR_ID, key_value="EPR-AAA")],
    )

    bulk_repo = BulkRepository(table_name=TABLE_NAME, dynamodb_client=dynamodb_client)
    transactions = bulk_repo.generate_transaction_statements(
        {"ProductTeam": product_team.state()}
    )
    bulk_repo.write(transactions)

    product_team_by_id = product_team_repo.read(product_team.id)
    product_team_by_key = product_team_repo.read("EPR-AAA")
    assert product_team == product_team_by_id
    assert product_team == product_team_by_key


def test_BulkRepository_handle_CpmProduct(dynamodb_client):
    product_repo = CpmProductRepository(
        table_name=TABLE_NAME, dynamodb_client=dynamodb_client
    )
    product_team = ProductTeam(name="my-product", ods_code="AAA")
    product = product_team.create_cpm_product(name="my-product")
    product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value="AAA-123456")
    product.clear_events()

    bulk_repo = BulkRepository(table_name=TABLE_NAME, dynamodb_client=dynamodb_client)
    transactions = bulk_repo.generate_transaction_statements(
        {"CpmProduct": product.state()}
    )
    bulk_repo.write(transactions)

    product_by_id = product_repo.read(product_team.id, product.id)
    product_by_key = product_repo.read(product_team.id, "AAA-123456")
    assert product == product_by_id
    assert product == product_by_key


def test_BulkRepository_handle_Device(dynamodb_client):
    device_repo = DeviceRepository(
        table_name=TABLE_NAME, dynamodb_client=dynamodb_client
    )
    product_team = ProductTeam(name="my-product", ods_code="AAA")
    product = product_team.create_cpm_product(name="my-product")
    device = product.create_device(name="my-product", environment=Environment.PROD)
    device.add_key(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value="123456")
    device.add_tag(party_key="123", something_else="456")
    device.clear_events()

    bulk_repo = BulkRepository(table_name=TABLE_NAME, dynamodb_client=dynamodb_client)
    transactions = bulk_repo.generate_transaction_statements({"Device": device.state()})
    bulk_repo.write(transactions)

    device_by_id = device_repo.read(
        product_team.id,
        product.id,
        Environment.PROD,
        device.id,
    )
    device_by_key = device_repo.read(
        product_team.id,
        product.id,
        Environment.PROD,
        "123456",
    )
    (device_by_tag,) = device_repo.query_by_tag(party_key="123", something_else="456")
    assert device == device_by_id
    assert device == device_by_key

    device.tags = set()  ## query_by_tag does not return tags
    assert device == device_by_tag


def test_BulkRepository_handle_DeviceReferenceData(dynamodb_client):
    device_ref_data_repo = DeviceReferenceDataRepository(
        table_name=TABLE_NAME, dynamodb_client=dynamodb_client
    )
    product_team = ProductTeam(name="my-product", ods_code="AAA")
    product = product_team.create_cpm_product(name="my-product")
    device_ref_data = product.create_device_reference_data(
        name="my-product", environment=Environment.PROD
    )

    bulk_repo = BulkRepository(table_name=TABLE_NAME, dynamodb_client=dynamodb_client)
    transactions = bulk_repo.generate_transaction_statements(
        {"DeviceReferenceData": device_ref_data.state()}
    )
    bulk_repo.write(transactions)

    device_ref_data_by_id = device_ref_data_repo.read(
        product_team.id, product.id, Environment.PROD, device_ref_data.id
    )
    assert device_ref_data == device_ref_data_by_id
