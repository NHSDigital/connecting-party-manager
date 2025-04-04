import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from builder.common import (
    BUILD_DIR,
    DIST_DIR,
    PROJECT_ROOT_DIR,
    SRC_DIR,
    clean_dir,
    copy_source_code,
    get_base_dir,
    zip_package,
)


@contextmanager
def create_zip_package(
    package_name: str, base_dir: Path
) -> Generator[Path, None, None]:
    dist_dir = base_dir / DIST_DIR
    build_dir = dist_dir / BUILD_DIR
    copy_dir = build_dir / Path(
        str(base_dir).replace(f"{PROJECT_ROOT_DIR}/{SRC_DIR}/", "")
    )

    clean_dir(dist_dir)
    print(f"Building {base_dir.parent.name}/{package_name}")  # noqa: T201
    yield copy_dir
    zip_package(build_dir)
    shutil.move(dist_dir / f"{BUILD_DIR}.zip", dist_dir / f"{package_name}.zip")
    clean_dir(build_dir)


def build(file):
    if "archived_epr" not in file:
        lambda_base_dir = get_base_dir(file)
        package_name = lambda_base_dir.name

        with create_zip_package(
            package_name=package_name, base_dir=lambda_base_dir
        ) as build_dir:
            copy_source_code(source_dir=lambda_base_dir, build_dir=build_dir)
