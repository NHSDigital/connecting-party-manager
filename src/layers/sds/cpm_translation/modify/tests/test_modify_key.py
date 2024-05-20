import pytest
from sds.cpm_translation.modify.modify_key import (
    InvalidModificationRequest,
    NotAnSdsKey,
    get_modify_key_function,
    new_accredited_system,
    replace_accredited_systems,
    replace_msg_handling_system,
)
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs


@pytest.mark.parametrize(
    ("model", "modification_type", "field", "result"),
    [
        (
            NhsAccreditedSystem,
            ModificationType.ADD,
            "nhs_as_client",
            new_accredited_system,
        ),
        (
            NhsAccreditedSystem,
            ModificationType.REPLACE,
            "nhs_as_client",
            replace_accredited_systems,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_mhs_party_key",
            replace_msg_handling_system,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_mhs_svc_ia",
            replace_msg_handling_system,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_id_code",
            replace_msg_handling_system,
        ),
    ],
)
def test_get_modify_key_function(model, modification_type, field, result):
    assert (
        get_modify_key_function(
            model=model, modification_type=modification_type, field=field
        )
        is result
    )


@pytest.mark.parametrize(
    ("model", "modification_type", "field"),
    [
        (NhsAccreditedSystem, ModificationType.DELETE, "nhs_as_client"),
        (NhsMhs, ModificationType.ADD, "nhs_mhs_party_key"),
        (NhsMhs, ModificationType.ADD, "nhs_mhs_svc_ia"),
        (NhsMhs, ModificationType.ADD, "nhs_id_code"),
        (NhsMhs, ModificationType.DELETE, "nhs_mhs_party_key"),
        (NhsMhs, ModificationType.DELETE, "nhs_mhs_svc_ia"),
        (NhsMhs, ModificationType.DELETE, "nhs_id_code"),
    ],
)
def test_get_modify_key_function_invalid(model, modification_type, field):
    with pytest.raises(InvalidModificationRequest):
        get_modify_key_function(
            model=model, modification_type=modification_type, field=field
        )


@pytest.mark.parametrize("model", (NhsAccreditedSystem, NhsMhs))
@pytest.mark.parametrize(
    "modification_type",
    (ModificationType.ADD, ModificationType.REPLACE, ModificationType.DELETE),
)
def test_get_modify_key_function_other(model, modification_type):
    with pytest.raises(NotAnSdsKey):
        get_modify_key_function(
            model=model, modification_type=modification_type, field="foo"
        )
