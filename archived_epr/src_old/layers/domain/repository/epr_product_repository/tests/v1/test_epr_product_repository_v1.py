import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.epr_product import EprProduct
from domain.core.root import Root
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from domain.repository.keys import TableKey
from domain.repository.marshall import marshall_value

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.dynamodb import mock_table
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.terraform import read_terraform_output
from test_helpers.uuid import consistent_uuid


def _create_product_team(name: str = "FOOBAR Product Team", ods_code: str = "F5H1R"):
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    return org.create_product_team_epr(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )


@pytest.mark.integration
def test__epr_product_repository(product: EprProduct, repository: EprProductRepository):
    repository.write(product)
    result = repository.read(product_team_id=product.product_team_id, id=product.id)
    assert result == product


@pytest.mark.integration
def test__epr_product_repository_already_exists(
    product: EprProduct, repository: EprProductRepository
):
    repository.write(product)
    with pytest.raises(AlreadyExistsError):
        repository.write(product)


@pytest.mark.integration
def test__epr_product_repository__product_does_not_exist(
    repository: EprProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, id=product_id)


def test__epr_product_repository_local(
    product: EprProduct, repository: EprProductRepository
):
    repository.write(product)
    result = repository.read(product_team_id=product.product_team_id, id=product.id)
    assert result == product


def test__epr_product_repository__product_does_not_exist_local(
    repository: EprProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, id=product_id)


@pytest.mark.integration
def test__query_products_by_product_team():
    product_team = _create_product_team()
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    repo = EprProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    product_id = ProductId.create()
    epr_product = product_team.create_epr_product(
        name="epr-product-name", product_id=product_id.id
    )
    repo.write(epr_product)
    product_id = ProductId.create()
    epr_product_2 = product_team.create_epr_product(
        name="epr-product-name-2", product_id=product_id.id
    )
    repo.write(epr_product_2)
    result = repo.search(product_team_id=product_team.id)
    assert len(result) == 2
    assert isinstance(result[0], EprProduct)
    assert isinstance(result[1], EprProduct)
    assert epr_product in result
    assert epr_product_2 in result


@pytest.mark.integration
def test__query_products_by_product_team_a():
    product_team_a = _create_product_team()
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    repo = EprProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    product_id = ProductId.create()
    epr_product = product_team_a.create_epr_product(
        name="epr-product-name", product_id=product_id.id
    )
    repo.write(epr_product)
    product_id = ProductId.create()
    epr_product_2 = product_team_a.create_epr_product(
        name="epr-product-name-2", product_id=product_id.id
    )
    repo.write(epr_product_2)
    product_team_b = _create_product_team(name="product_team_b", ods_code="CBA")
    product_id = ProductId.create()
    epr_product_3 = product_team_b.create_epr_product(
        name="epr-product-name-3", product_id=product_id.id
    )
    repo.write(epr_product_3)
    result = repo.search(product_team_id=product_team_a.id)
    assert len(result) == 2
    assert isinstance(result[0], EprProduct)
    assert isinstance(result[1], EprProduct)
    assert epr_product in result
    assert epr_product_2 in result


@pytest.mark.integration
def test__query_products_by_product_team_with_sk_prefix():
    product_team = _create_product_team()
    table_name = read_terraform_output("dynamodb_epr_table_name.value")

    product_id = ProductId.create()
    repo = EprProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    epr_product = product_team.create_epr_product(
        name="epr-product-name", product_id=product_id.id
    )
    repo.write(epr_product)
    product_id = ProductId.create()
    epr_product_2 = product_team.create_epr_product(
        name="epr-product-name-2", product_id=product_id.id
    )
    repo.write(epr_product_2)

    pk = TableKey.PRODUCT_TEAM.key(product_team.id)
    sk = "FOO#1234"
    args = {
        "TableName": table_name,
        "Item": {
            "pk": marshall_value(pk),
            "sk": marshall_value(sk),
        },
    }
    client = dynamodb_client()
    client.put_item(**args)

    result = repo.search(product_team_id=product_team.id)
    assert len(result) == 2
    assert isinstance(result[0], EprProduct)
    assert isinstance(result[1], EprProduct)
    assert epr_product in result
    assert epr_product_2 in result


def test__epr_product_repository_search():
    product_id = "P.XXX-YYY"

    product_team = _create_product_team()
    epr_product = product_team.create_epr_product(
        name="epr-product-name", product_id=product_id
    )

    with mock_table("my_table") as client:
        repo = EprProductRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        repo.write(epr_product)
        result = repo.search(product_team_id=product_team.id)

    assert result == [epr_product]
