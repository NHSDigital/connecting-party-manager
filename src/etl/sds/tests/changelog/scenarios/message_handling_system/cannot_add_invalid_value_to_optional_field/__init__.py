from etl.sds.tests.changelog.utils import (
    ADD_MESSAGE_HANDLING_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_ADD_NHS_MHS_ACK_REQUESTED = create_modify_ldif(
    "add/nhs_mhs_ack_requested.InvalidValue.ldif", device_type="message_handling_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        _ADD_NHS_MHS_ACK_REQUESTED,
    ],
)
