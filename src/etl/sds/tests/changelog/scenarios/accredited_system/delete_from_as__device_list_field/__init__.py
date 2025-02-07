from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    MODIFY_ACCREDITED_SYSTEM_ADD_TO_CAT_BAG,
    MODIFY_ACCREDITED_SYSTEM_DELETE_CAT_BAG,
    _Scenario,
)

# add cat bag field
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM,
        MODIFY_ACCREDITED_SYSTEM_ADD_TO_CAT_BAG,
        MODIFY_ACCREDITED_SYSTEM_DELETE_CAT_BAG,
    ],
)
