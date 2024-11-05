from event.json import json_load

from .constants import PROJECT_ROOT

PATH_TO_CORE_CPM_TEST_DATA = (
    PROJECT_ROOT / "src/layers/domain/request_models/tests/data"
)


def _read_core_test_data(file_name: str) -> dict | list:
    with open(file_name) as f:
        return json_load(f)


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
CPM_PRODUCT = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-example.json"
)
CPM_PRODUCT_EXTRA_PARAMS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-product-example-extra.json"
)
CPM_DEVICE = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-device-example.json"
)
CPM_DEVICE_EXTRA_PARAMS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-device-example-extra.json"
)
CPM_DEVICE_REFERENCE_DATA = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-device-reference-data-example.json"
)
CPM_DEVICE_REFERENCE_DATA_EXTRA_PARAMS = _read_core_test_data(
    f"{PATH_TO_CORE_CPM_TEST_DATA}/cpm-device-reference-data-example-extra.json"
)
