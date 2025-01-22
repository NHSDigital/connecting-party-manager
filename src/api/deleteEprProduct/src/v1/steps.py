from http import HTTPStatus

<<<<<<<< HEAD:src/api/deleteEprProduct/src/v1/steps.py
from domain.api.common_steps.read_epr_product import before_steps, read_product
from domain.core.epr_product import EprProduct
from domain.repository.epr_product_repository import EprProductRepository
========
from domain.api.common_steps.read_cpm_product import before_steps, read_product
from domain.core.cpm_product import CpmProduct
from domain.repository.cpm_product_repository import CpmProductRepository
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/deleteCpmProduct/src/v1/steps.py


def delete_product(data, cache) -> EprProduct:
    product: EprProduct = data[read_product]
    product_repo: EprProductRepository = EprProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product.delete()
    return product_repo.write(product)


def set_http_status(data, cache) -> tuple[int, None]:
    return HTTPStatus.NO_CONTENT, None


steps = [
    *before_steps,
    delete_product,
    set_http_status,
]
