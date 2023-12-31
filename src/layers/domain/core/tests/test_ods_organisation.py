import pytest
from domain.core.ods_organisation import OdsOrganisation
from domain.core.root import Root
from pydantic import ValidationError


@pytest.mark.parametrize(
    "ods_code,name",
    [
        ["F5H1R", "ROYAL DERBY HOSPITAL UTC"],
        ["RTG09", "QUEENS MEDICAL CENTRE"],
        ["NLF02", "THE ROYAL OLDHAM HOSPITAL - PHYSIOTHERAPY DEPARTMENT"],
    ],
)
def test__can_instantiate_ods_organisation(ods_code: str, name: str):
    result = Root.create_ods_organisation(ods_code=ods_code)

    assert isinstance(result, OdsOrganisation)
    assert result.ods_code == ods_code


@pytest.mark.parametrize(
    "ods_code",
    [
        "ABCDEFGHIJ",
        "!@£$%",
    ],
)
def test__id_must_be_ods_code(ods_code: str):
    with pytest.raises(ValidationError):
        Root.create_ods_organisation(ods_code=ods_code)
