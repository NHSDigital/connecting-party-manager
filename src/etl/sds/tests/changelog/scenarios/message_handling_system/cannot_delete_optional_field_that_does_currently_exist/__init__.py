from etl.sds.tests.changelog.utils import (
    ADD_MESSAGE_HANDLING_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_DELETE_NHS_MHS_ACK_REQUESTED = create_modify_ldif(
    "delete/nhs_mhs_ack_requested.ldif", device_type="message_handling_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        _DELETE_NHS_MHS_ACK_REQUESTED,
    ],
)
