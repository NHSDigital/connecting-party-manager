from http import HTTPStatus

from domain.common_steps.read_product import before_steps, read_product
from domain.core.cpm_product import CpmProduct
from domain.repository.cpm_product_repository.v3 import CpmProductRepository


def delete_product(data, cache) -> CpmProduct:
    product: CpmProduct = data[read_product]
    product_repo: CpmProductRepository = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product.delete()
    return product_repo.write(product)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.NO_CONTENT


steps = [
    *before_steps,
    delete_product,
    set_http_status,
]
