from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    MODIFY_ACCREDITED_SYSTEM_REPLACE_INTERACTIONS_FIELD,
    _Scenario,
)

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM,
        MODIFY_ACCREDITED_SYSTEM_REPLACE_INTERACTIONS_FIELD,
    ],
)
