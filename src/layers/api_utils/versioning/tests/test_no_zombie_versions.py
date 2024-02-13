from importlib import import_module
from pathlib import Path
from types import FunctionType
from unittest import mock

import pytest
from api_utils.versioning.constants import VERSION_RE

from test_helpers.constants import PROJECT_ROOT

API_ROOT_DIRNAME = "api"
VERSIONED_HANDLER_GLOB = "src/v*/steps.py"
API_LAMBDAS = set((PROJECT_ROOT / "src" / API_ROOT_DIRNAME).iterdir()) - set(
    [
        PROJECT_ROOT / "src" / API_ROOT_DIRNAME / "authoriser",
        PROJECT_ROOT / "src" / API_ROOT_DIRNAME / "status",
    ]
)


def _module_path_from_file_path(file_path: Path, api_root_dirname=API_ROOT_DIRNAME):
    path = str(file_path.parent / file_path.stem)
    path_relative_to_api_root = Path(path[path.find(api_root_dirname) :])
    return ".".join(path_relative_to_api_root.parts)


def get_steps_by_version(
    index_file_path: Path, api_root_dirname=API_ROOT_DIRNAME
) -> dict[str, list[FunctionType]]:
    versions_paths = index_file_path.parent.glob(VERSIONED_HANDLER_GLOB)
    versioned_steps = {}
    for file_path in versions_paths:
        (version_number,) = VERSION_RE.match(file_path.parent.name).groups()
        module_path = _module_path_from_file_path(
            file_path, api_root_dirname=api_root_dirname
        )
        versioned_handler = import_module(module_path)
        versioned_steps[version_number] = versioned_handler.steps
    return versioned_steps


@mock.patch.dict(
    "os.environ",
    {
        "DYNAMODB_TABLE": "hiya",
        "AWS_DEFAULT_REGION": "eu-west-2",
    },
    clear=True,
)
@pytest.mark.parametrize("api", API_LAMBDAS)
def test_no_zombie_versions(api: Path):
    index_file_path = api / "index.py"
    api_index_module_path = _module_path_from_file_path(index_file_path)
    api_index = import_module(api_index_module_path)
    versioned_steps = get_steps_by_version(index_file_path=index_file_path)
    assert (
        api_index.versioned_steps == versioned_steps
    ), f"'versioned_steps' in {api} is not consistent with the steps for this API"


def test_zombie_versions():
    index_file_path = Path(__file__).parent / "example_api" / "index.py"
    api_index_module_path = _module_path_from_file_path(
        index_file_path, api_root_dirname="api_utils"
    )
    api_index = import_module(api_index_module_path)
    versioned_steps = get_steps_by_version(
        index_file_path=index_file_path, api_root_dirname="api_utils"
    )
    assert api_index.versioned_steps != versioned_steps
