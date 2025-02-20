from etl.sds.tests.changelog.utils import (
    ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM,
    ADD_MESSAGE_HANDLING_SYSTEM,
    DELETE_MESSAGE_HANDLING_SYSTEM,
    _Scenario,
)

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
        ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM,
        DELETE_MESSAGE_HANDLING_SYSTEM,
    ],
)
