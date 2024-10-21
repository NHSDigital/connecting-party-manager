from event.json import json_load

from .constants import PROJECT_ROOT

PATH_TO_CORE_TEST_DATA = PROJECT_ROOT / "src/layers/domain/fhir_translation/tests/data"
PATH_TO_CORE_CPM_TEST_DATA = (
    PROJECT_ROOT / "src/layers/domain/request_models/tests/data"
)


def _read_core_test_data(file_name: str) -> dict | list:
    with open(file_name) as f:
        return json_load(f)


# ORGANISATION = _read_core_test_data(
#     f"{PATH_TO_CORE_TEST_DATA}/organization-fhir-example-required.json"
# )
DEVICE = _read_core_test_data(
    f"{PATH_TO_CORE_TEST_DATA}/device-fhir-example-required.json"
)
FAILED_DEVICE = _read_core_test_data(
    f"{PATH_TO_CORE_TEST_DATA}/device-fhir-failure-example-required.json"
)
CPM_PRODUCT_TEAM_ID = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-id.json"
)
CPM_PRODUCT_TEAM_NO_ID = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-no-id.json"
)
CPM_PRODUCT_TEAM_NO_ID_NO_KEYS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-no-id-no-keys.json"
)
CPM_PRODUCT_TEAM_NO_ID_KEYS_NOT_ALLOWED = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-no-id-keys-not-allowed.json"
)
CPM_PRODUCT_TEAM_NO_ID_DUPED_KEYS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-no-id-duped-keys.json"
)
CPM_PRODUCT_TEAM_EXTRA_PARAMS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-team-example-extra.json"
)
