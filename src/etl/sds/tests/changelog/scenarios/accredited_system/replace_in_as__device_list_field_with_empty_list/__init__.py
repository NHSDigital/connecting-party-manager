from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM_WITH_ACF,
    MODIFY_ACCREDITED_SYSTEM_REPLACE_DEVICE_LIST_FIELD_WITH_EMPTY,
    _Scenario,
)

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM_WITH_ACF,
        MODIFY_ACCREDITED_SYSTEM_REPLACE_DEVICE_LIST_FIELD_WITH_EMPTY,
    ],
)
