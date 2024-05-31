from etl.sds.tests.changelog.utils import (
    ADD_ACCREDITED_SYSTEM,
    _Scenario,
    create_modify_ldif,
)

_ADD_NHS_AS_CLIENT = create_modify_ldif(
    "add/nhs_as_client.ldif", device_type="accredited_system"
)
_DELETE_NHS_PRODUCT_NAME = create_modify_ldif(
    "delete/nhs_product_name.ldif", device_type="accredited_system"
)
_ADD_NHS_PRODUCT_NAME = create_modify_ldif(
    "add/nhs_product_name.ldif", device_type="accredited_system"
)
SCENARIO = _Scenario(
    file_path=__file__,
    extract_input=[
        ADD_ACCREDITED_SYSTEM,
        _ADD_NHS_AS_CLIENT,
        _DELETE_NHS_PRODUCT_NAME,
        _ADD_NHS_PRODUCT_NAME,
    ],
)
