from etl.sds.tests.changelog.utils import (
    ADD_MESSAGE_HANDLING_SYSTEM,
    MODIFY_MESSAGE_HANDLING_SYSTEM_DELETE_MESSAGE_SETS_FIELD,
    _Scenario,
)

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        MODIFY_MESSAGE_HANDLING_SYSTEM_DELETE_MESSAGE_SETS_FIELD,
    ],
)
