import shutil
import tomllib
from pathlib import Path

from builder.third_party_build import build_third_party

from test_helpers.constants import PROJECT_ROOT

PYPROJECT_TOML = "pyproject.toml"
PATH_TO_DIST = Path(__file__).parent.parent / "dist"
PATH_TO_PREVIOUS_PYPROJECT_TOML = PATH_TO_DIST / PYPROJECT_TOML
PATH_TO_CURRENT_PYPROJECT_TOML = PROJECT_ROOT / PYPROJECT_TOML
DEV_GROUPS = {"dev", "local"}


def parse_groups(pyproject_toml_path) -> dict[str, dict[str, str]]:
    if not Path(pyproject_toml_path).exists():
        return {}
    with open(pyproject_toml_path, "rb") as f:
        pyproject = tomllib.load(f)
    poetry_config: dict[str, dict] = pyproject["tool"]["poetry"]

    core_dependencies = poetry_config["dependencies"]
    core = {"core": core_dependencies}

    dependency_groups = {
        group: {**core_dependencies, **config["dependencies"]}
        for group, config in poetry_config["group"].items()
        if group not in DEV_GROUPS
    }

    return {**core, **dependency_groups}


if __name__ == "__main__":
    old_groups = parse_groups(PATH_TO_PREVIOUS_PYPROJECT_TOML)
    current_groups = parse_groups(PATH_TO_CURRENT_PYPROJECT_TOML)

    any_change_detected = False
    for group, dependencies in current_groups.items():
        path_to_zip = PATH_TO_DIST / f"third_party_{group}.zip"
        change_detected = old_groups.get(group) != dependencies
        any_change_detected = any_change_detected or change_detected
        if (
            not path_to_zip.exists()
            or not PATH_TO_PREVIOUS_PYPROJECT_TOML.exists()
            or change_detected
        ):
            build_third_party(
                file=__file__,
                pyproject_toml_path=PATH_TO_CURRENT_PYPROJECT_TOML,
                group=group,
                dependencies=dependencies,
            )
        else:
            print(  # noqa: T201
                f"Skipping rebuild of {path_to_zip} since no changes detected to group '{group}'"
            )

    if any_change_detected:
        shutil.copy(
            src=PATH_TO_CURRENT_PYPROJECT_TOML, dst=PATH_TO_PREVIOUS_PYPROJECT_TOML
        )
