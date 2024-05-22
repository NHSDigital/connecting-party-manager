from pathlib import Path

import pytest

PATH_TO_HERE = Path(__file__).parent
PATH_TO_ROOT = PATH_TO_HERE.parent.parent
PATH_TO_COPIED_PUBLIC_SWAGGER = PATH_TO_HERE.parent / "swagger.yaml"
PATH_TO_DIST_PUBLIC_SWAGGER = (
    PATH_TO_ROOT.parent
    / "infrastructure"
    / "swagger"
    / "dist"
    / "public"
    / "swagger.yaml"
)

# Should this test be failing, you need to copy the new swagger file from dist into this public_swagger location
# This is just a version controlled version of that file.


@pytest.mark.unit
def test_swagger_public_matches_dist():
    dist_swagger_file = PATH_TO_DIST_PUBLIC_SWAGGER
    copied_swagger_file = PATH_TO_COPIED_PUBLIC_SWAGGER

    with open(dist_swagger_file, "r") as file1, open(copied_swagger_file, "r") as file2:
        content1 = file1.read()
        content2 = file2.read()

    assert content1 == content2, "Swagger files are not identical"
