from etl.sds.tests.changelog.utils import ADD_MESSAGE_HANDLING_SYSTEM, _Scenario

SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_MESSAGE_HANDLING_SYSTEM,
    ],
)
