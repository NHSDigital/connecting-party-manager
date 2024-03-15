import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import sh

from .common import copy_source_code, get_base_dir
from .layer_build import create_temp_path, create_zip_package

REQUIREMENTS = "requirements.txt"
VENV = "venv"


def loosen_requirement(requirement: str):
    """
    Since non-linux and linux environments aren't guaranteed to have the same
    package versions, we loosen the version requirement for non-linux distros here.
    """
    return requirement.replace("==", "~=")


def create_requirements(
    root_dir: Path,
    pyproject_toml_path: Path,
    group: str,
    dependencies: dict[str, str],
    requirements_name: str = REQUIREMENTS,
) -> Path:
    shutil.copy(pyproject_toml_path, root_dir)
    group_filter = tuple() if group == "core" else ("--with", group)
    raw_requirements = sh.poetry(
        "export",
        "-f",
        requirements_name,
        "--without-hashes",
        *group_filter,
        _cwd=root_dir,
    )
    individual_requirements = str(raw_requirements).split("\n")[:-1]
    filtered_requirements = [
        line
        for line in individual_requirements
        if any(map(line.startswith, dependencies))
    ]
    looser_individual_requirements = map(loosen_requirement, filtered_requirements)
    with open(root_dir / requirements_name, "w") as f:
        data = "\n".join(looser_individual_requirements)
        f.write(data)
    return requirements_name


def docker_run(docker_file: Path, root_dir: Path, group: str):
    for source_file in docker_file.parent.iterdir():
        shutil.copy(source_file, root_dir)
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    image_name = f"{group}:latest"
    sh.docker(
        "build",
        ".",
        "--tag",
        image_name,
        "--build-arg",
        f"PYTHON_VERSION={python_version}",
        _cwd=root_dir,
    )
    sh.docker(
        "run",
        "-v",
        f"{root_dir}:/var/task",
        image_name,
        "/bin/bash",
        "-c",
        (
            "pip install -r requirements.txt -t $PWD/venv;"
            "cp /usr/extras/* $PWD/venv;"
            'chown -R `stat -c "%u:%g" $PWD/venv` $PWD/venv;'
            "exit;"
        ),
        _cwd=root_dir,
    )


def get_dockerfile_path(base_dir: Path, group: str):
    dockerfile_basedir = base_dir / "dockerfiles"
    dockerfile_dir = dockerfile_basedir / "default"
    for path in dockerfile_basedir.iterdir():
        if path.name == group:
            dockerfile_dir = path
    return dockerfile_dir / "Dockerfile"


def build_third_party(
    file: str,
    pyproject_toml_path: Path,
    group: str,
    dependencies: dict[str, str],
):
    base_dir = get_base_dir(file)
    package_zipper = create_zip_package(
        package_name=f"third_party_{group}", base_dir=base_dir, third_party=True
    )
    docker_file = get_dockerfile_path(base_dir=base_dir, group=group)

    with TemporaryDirectory() as root_dir, package_zipper as build_dir:
        root_dir = Path(root_dir).resolve()
        venv_dir = root_dir / VENV
        with create_temp_path(path=venv_dir, is_dir=True):
            create_requirements(
                root_dir=root_dir,
                pyproject_toml_path=pyproject_toml_path,
                group=group,
                dependencies=dependencies,
            )
            docker_run(docker_file=docker_file, root_dir=root_dir, group=group)
            copy_source_code(source_dir=venv_dir, build_dir=build_dir)
