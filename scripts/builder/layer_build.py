import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from builder.common import (
    BUILD_DIR,
    DIST_DIR,
    clean_dir,
    copy_source_code,
    get_base_dir,
    zip_package,
)

UNNECESSARY_DIRS = [
    "**/__pycache__/*",
    "*.dist-info",
    "*tests",
    "botocore",
    "boto3",
    "**/pydantic/*.so",
    "_pytest",
]


@contextmanager
def create_zip_package(
    package_name: str, base_dir: Path, third_party=False
) -> Generator[Path, None, None]:
    dist_dir = base_dir / DIST_DIR
    build_dir = dist_dir / BUILD_DIR
    zip_path = dist_dir / f"{package_name}.zip"
    package_dir = build_dir / "python"
    if third_party:
        clean_dir(build_dir)
        zip_path.unlink(missing_ok=True)
    else:
        package_dir = package_dir / package_name
        clean_dir(dist_dir)

    print(f"Building {package_name}")  # noqa: T201
    yield package_dir
    zip_package(build_dir)
    shutil.move(dist_dir / f"{BUILD_DIR}.zip", zip_path)

    clean_dir(build_dir)


def build(file):
    layer_base_dir = get_base_dir(file)
    package_name = layer_base_dir.name

    with create_zip_package(
        package_name=package_name, base_dir=layer_base_dir
    ) as build_dir:
        copy_source_code(source_dir=layer_base_dir, build_dir=build_dir)


@contextmanager
def create_temp_path(path: Path, is_dir: bool) -> Generator[Path, None, None]:
    error = None
    try:
        if is_dir:
            path.mkdir(parents=True)
        else:
            path.touch()
        yield
    except Exception as err:
        error = err
    finally:
        if is_dir:
            shutil.rmtree(path)
        else:
            path.unlink()
    if error:
        raise error


def clean_unnecessary_files(directory: Path):
    for pattern in UNNECESSARY_DIRS:
        for filename in Path(directory).glob(pattern):
            if filename.is_dir():
                shutil.rmtree(filename)
            else:
                filename.unlink()
