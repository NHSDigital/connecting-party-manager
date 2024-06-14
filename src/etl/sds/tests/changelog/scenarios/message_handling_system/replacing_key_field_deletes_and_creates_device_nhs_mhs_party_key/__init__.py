from etl.sds.tests.changelog.utils import (
    ADD_MESSAGE_HANDLING_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_REPLACE_NHS_MHS_PARTY_KEY = create_modify_ldif(
    "replace/nhs_mhs_party_key.ldif", device_type="message_handling_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        _REPLACE_NHS_MHS_PARTY_KEY,
    ],
)
