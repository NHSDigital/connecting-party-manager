from contextlib import nullcontext as does_not_raise

import pytest
from pydantic import ValidationError
from sds.domain.organizational_unit import OrganizationalUnitDistinguishedName
from sds.domain.sds_modification_request import SdsModificationRequest


@pytest.mark.parametrize(
    ["field_name", "raises"],
    (
        [
            "uniqueidentifier",
            pytest.raises(ValidationError),
        ],
        [
            "foo",
            does_not_raise(),
        ],
    ),
)
def test_immutable_field_error(field_name, raises):
    with raises:
        SdsModificationRequest(
            distinguished_name=OrganizationalUnitDistinguishedName(
                ou="services", o="nhs", uniqueidentifier=""
            ),
            objectclass={"modify"},
            changetype={"add"},
            uniqueidentifier={"123"},
            modifications=[("add", field_name, {"a", "b"})],
        )
