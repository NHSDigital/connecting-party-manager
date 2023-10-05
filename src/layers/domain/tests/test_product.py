from typing import Set
import pytest
from domain import Product, DuplicateError


@pytest.mark.parametrize(
    ["id", "name", "questionnaires", "dependency_questionnaires"],
    [
        ["foo", "Foo", [], []],
        ["bah", "Bah", ["x"], []],
        ["meep", "Meep", [], []],
    ],
)
def test__can_create_product(
    id: str, name: str, questionnaires: Set[str], dependency_questionnaires: Set[str]
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
    assert (
        result._dependency_questionnaires == set(dependency_questionnaires)
    ), "Dependency Questionnaires"
