from contextlib import nullcontext as do_not_raise

import pytest
from domain.core.root.v2 import Root
from pydantic import ValidationError


@pytest.mark.parametrize(
    "ods_code",
    ["F5H1R", "RTG09", "NLF02", "D82007002"],
)
def test__can_instantiate_ods_organisation(ods_code: str):
    with do_not_raise():
        Root.create_ods_organisation(ods_code=ods_code)


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
