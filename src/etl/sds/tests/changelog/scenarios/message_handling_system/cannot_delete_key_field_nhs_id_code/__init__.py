from etl.sds.tests.changelog.utils import (
    ADD_MESSAGE_HANDLING_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_ADD_NHS_ID_CODE = create_modify_ldif(
    "delete/nhs_id_code.ldif", device_type="message_handling_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        _ADD_NHS_ID_CODE,
    ],
)
