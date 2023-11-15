import sys
from enum import StrEnum, auto
from os.path import getsize
from pathlib import Path

PATH_TO_HERE = Path(__file__).parent
PATH_TO_ROOT = PATH_TO_HERE.parent.parent
PATH_TO_CHANGELOG_DIR = PATH_TO_ROOT / "changelog"
PATH_TO_ROOT_CHANGELOG_FILE = PATH_TO_ROOT / "CHANGELOG.md"


class Result(StrEnum):
    UPDATED = auto()
    FILE_NOT_FOUND = auto()
    NOTHING_TO_DO = auto()


def main(branch: str) -> Result:
    PATH_TO_ROOT_CHANGELOG_FILE.touch()
    release_date = branch.replace("release/", "")

    file_list = sorted(
        filter(
            Path.is_file,
            PATH_TO_CHANGELOG_DIR.iterdir(),
        ),
        reverse=True,
    )

    if release_date not in (f.stem for f in file_list):
        return Result.FILE_NOT_FOUND

    changelog_content = ["# Changelog\n"]
    for file_path in file_list:
        changelog_content.append(f"## {file_path.stem}")
        with open(file_path, "r") as f:
            changelog_content.append(f.read())
    changelog_data = "\n".join(changelog_content)

    with open(PATH_TO_ROOT_CHANGELOG_FILE, "r") as f:
        original_changelog_data = f.read()

    with open(PATH_TO_ROOT_CHANGELOG_FILE, "w") as f:
        f.write(changelog_data)

    if original_changelog_data != changelog_data:
        return Result.UPDATED
    return Result.NOTHING_TO_DO


if __name__ == "__main__":
    (branch,) = sys.argv[1:]
    result = main(branch)
    print(result.value)
