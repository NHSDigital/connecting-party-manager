import pytest
from domain.core.error import InvalidOdsCodeError
from domain.core.product import OdsOrganisation
from domain.core.root import Root


@pytest.mark.slow
@pytest.mark.parametrize(
    "id,name",
    [
        ["F5H1R", "ROYAL DERBY HOSPITAL UTC"],
        ["RTG09", "QUEENS MEDICAL CENTRE"],
        ["NLF02", "THE ROYAL OLDHAM HOSPITAL - PHYSIOTHERAPY DEPARTMENT"],
    ],
)
def test__can_instantiate_ods_organisation(id: str, name: str):
    result = Root.create_ods_organisation(id, name)

    assert isinstance(result, OdsOrganisation)
    assert result.id == id
    assert result.name == name


@pytest.mark.slow
@pytest.mark.parametrize(
    "id,name",
    [
        ["ABCDEFGHIJ", "Blah"],
        ["!@£$%", "Blah"],
    ],
)
def test__id_must_be_ods_code(id: str, name: str):
    with pytest.raises(InvalidOdsCodeError):
        Root.create_ods_organisation(id, name)
