from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    ADD_ANOTHER_ACCREDITED_SYSTEM_IN_SAME_PRODUCT,
    DELETE_ACCREDITED_SYSTEM,
    _Scenario,
)

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM,
        ADD_ANOTHER_ACCREDITED_SYSTEM_IN_SAME_PRODUCT,
        DELETE_ACCREDITED_SYSTEM,
    ],
)
