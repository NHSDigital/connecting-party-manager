import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound

from test_helpers.uuid import consistent_uuid


def _create_product_team(
    seed: int = 1, name: str = "product-team-name", ods_code: str = "ABC"
):
    org = Root.create_ods_organisation(ods_code=ods_code)
    return org.create_product_team(id=consistent_uuid(seed), name=name)


@pytest.mark.integration
def test__cpm_product_repository(product: CpmProduct, repository: CpmProductRepository):
    repository.write(product)
    result = repository.read(
        product_team_id=product.product_team_id, product_id=product.id
    )
    assert result == product


@pytest.mark.integration
def test__cpm_product_repository_already_exists(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)
    with pytest.raises(AlreadyExistsError):
        repository.write(product)


@pytest.mark.integration
def test__cpm_product_repository__product_does_not_exist(
    repository: CpmProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, product_id=product_id)


def test__cpm_product_repository_local(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)
    result = repository.read(
        product_team_id=product.product_team_id, product_id=product.id
    )
    assert result == product


def test__cpm_product_repository__product_does_not_exist_local(
    repository: CpmProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, product_id=product_id)


@pytest.mark.integration
def test__query_products_by_product_team():
    product_team = _create_product_team()
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    product_id = ProductId.create()
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id.id
    )
    repo.write(cpm_product)
    product_id = ProductId.create()
    cpm_product_2 = product_team.create_cpm_product(
        name="cpm-product-name-2", product_id=product_id.id
    )
    repo.write(cpm_product_2)
    result = repo.query_products_by_product_team(product_team_id=product_team.id)
    assert len(result) == 2
    assert isinstance(result[0], CpmProduct)
    assert isinstance(result[1], CpmProduct)
    assert cpm_product in result
    assert cpm_product_2 in result


@pytest.mark.integration
def test__query_products_by_product_team_a():
    product_team_a = _create_product_team()
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    product_id = ProductId.create()
    cpm_product = product_team_a.create_cpm_product(
        name="cpm-product-name", product_id=product_id.id
    )
    repo.write(cpm_product)
    product_id = ProductId.create()
    cpm_product_2 = product_team_a.create_cpm_product(
        name="cpm-product-name-2", product_id=product_id.id
    )
    repo.write(cpm_product_2)
    product_team_b = _create_product_team(seed=2, name="product_team_b", ods_code="CBA")
    product_id = ProductId.create()
    cpm_product_3 = product_team_b.create_cpm_product(
        name="cpm-product-name-3", product_id=product_id.id
    )
    repo.write(cpm_product_3)
    result = repo.query_products_by_product_team(product_team_id=product_team_a.id)
    assert len(result) == 2
    assert isinstance(result[0], CpmProduct)
    assert isinstance(result[1], CpmProduct)
    assert cpm_product in result
    assert cpm_product_2 in result


@pytest.mark.integration
def test__query_products_by_product_team_with_sk_prefix():
    product_team = _create_product_team()
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    product_id = ProductId.create()
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id.id
    )
    repo.write(cpm_product)
    product_id = ProductId.create()
    cpm_product_2 = product_team.create_cpm_product(
        name="cpm-product-name-2", product_id=product_id.id
    )
    repo.write(cpm_product_2)

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

    result = repo.query_products_by_product_team(product_team_id=product_team.id)
    assert len(result) == 2
    assert isinstance(result[0], CpmProduct)
    assert isinstance(result[1], CpmProduct)
    assert cpm_product in result
    assert cpm_product_2 in result


def test__cpm_product_repository_search():
    product_id = "P.XXX-YYY"

    product_team = _create_product_team()
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id
    )

    with mock_table("my_table") as client:
        repo = CpmProductRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        repo.write(cpm_product)
        result = repo.query_products_by_product_team(product_team_id=product_team.id)

    assert result == [cpm_product]
