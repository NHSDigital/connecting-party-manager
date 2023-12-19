from event.json import json_load

from .constants import PROJECT_ROOT

PATH_TO_CORE_TEST_DATA = PROJECT_ROOT / "src/layers/domain/fhir_translation/tests/data"


def _read_core_test_data(file_name: str) -> dict | list:
    with open(PATH_TO_CORE_TEST_DATA / file_name) as f:
        return json_load(f)


ORGANISATION = _read_core_test_data("organization-fhir-example-required.json")
DEVICE = _read_core_test_data("device-fhir-example-required.json")
