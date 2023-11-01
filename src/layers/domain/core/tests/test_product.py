from unittest import mock

import pytest
from domain.core.product import Product


@mock.patch("domain.core.product.validate_product_id_or_asid")
@pytest.mark.parametrize(
    ["id", "name", "questionnaires", "dependency_questionnaires"],
    [
        ["foo", "Foo", [], []],
        ["bah", "Bah", ["x"], []],
        ["meep", "Meep", [], []],
    ],
)
def test__can_create_product(
    mocked_validate_product_id_or_asid,
    id: str,
    name: str,
    questionnaires: set[str],
    dependency_questionnaires: set[str],
):
    result = Product(
        id,
        name,
        questionnaires=questionnaires,
        dependency_questionnaires=dependency_questionnaires,
    )

    assert result is not None, "Result"
    assert result.name == name, "Name"
    assert result._questionnaires == set(questionnaires), "Questionnaires"
    assert result._dependency_questionnaires == set(
        dependency_questionnaires
    ), "Dependency Questionnaires"
