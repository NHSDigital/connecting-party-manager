from http import HTTPStatus

from domain.api.common_steps.read_cpm_product import before_steps, read_product
from domain.core.cpm_product import CpmProduct
from domain.repository.cpm_product_repository import CpmProductRepository


def delete_product(data, cache) -> CpmProduct:
    product: CpmProduct = data[read_product]
    product_repo: CpmProductRepository = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product.delete()
    return product_repo.write(product)


def set_http_status(data, cache) -> tuple[int, None]:
    product: CpmProduct = data[read_product]
    return HTTPStatus.OK, {
        "code": "RESOURCE_DELETED",
        "message": f"{product.id} has been deleted.",
    }


steps = [
    *before_steps,
    delete_product,
    set_http_status,
]
