from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_ADD_NHS_AS_CLIENT = create_modify_ldif(
    "add/nhs_as_client.ldif", device_type="accredited_system"
)
_REPLACE_NHS_APPROVER_URP = create_modify_ldif(
    "replace/nhs_approver_urp.TooManyValues.ldif", device_type="accredited_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM,
        _ADD_NHS_AS_CLIENT,
        _REPLACE_NHS_APPROVER_URP,
    ],
)
