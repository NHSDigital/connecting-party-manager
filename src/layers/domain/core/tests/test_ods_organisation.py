import pytest
from domain.core.ods_organisation import OdsOrganisation
from domain.core.root import Root


@pytest.mark.parametrize(
    "id,name",
    [
        ["F5H1R", "ROYAL DERBY HOSPITAL UTC"],
        ["RTG09", "QUEENS MEDICAL CENTRE"],
        ["PN103", "THE ROYAL OLDHAM HOSPITAL"],
    ],
)
def test__can_instantiate_ods_organisation(id: str, name: str):
    result = Root.create_ods_organisation(id, name)

    assert isinstance(result, OdsOrganisation), "OdsOrganisation instantiated"
    assert result.id == id, "Id set"
    assert result.name == name, "Name set"


@pytest.mark.parametrize(
    "id,name",
    [
        ["ABCDEFGHIJ", "Blah"],
        ["!@£$%", "Blah"],
    ],
)
def test__id_must_be_ods_code(id: str, name: str):
    with pytest.raises(AssertionError):
        Root.create_ods_organisation(id, name)
