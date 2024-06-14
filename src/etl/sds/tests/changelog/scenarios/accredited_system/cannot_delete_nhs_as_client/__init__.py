from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_DELETE_NHS_AS_CLIENT = create_modify_ldif(
    "delete/nhs_as_client.ldif", device_type="accredited_system"
)
SCENARIO = _Scenario(
    file_path=__file__, extract_input=[ADD_ACCREDITED_SYSTEM, _DELETE_NHS_AS_CLIENT]
)
