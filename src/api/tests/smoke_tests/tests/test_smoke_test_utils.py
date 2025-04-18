import pytest

from api.tests.smoke_tests.utils import get_base_url


@pytest.mark.parametrize(
    ["workspace", "environment", "base_url"],
    [
        (
            "dev",
            "dev",
            "https://internal-dev.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "dev-sandbox",
            "dev",
            "https://internal-dev-sandbox.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "qa",
            "qa",
            "https://internal-qa.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "qa-sandbox",
            "qa",
            "https://internal-qa-sandbox.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "ref",
            "ref",
            "https://ref.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "int",
            "int",
            "https://int.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "int-sandbox",
            "int",
            "https://sandbox.api.service.nhs.uk/connecting-party-manager",
        ),
        (
            "prod",
            "prod",
            "https://api.service.nhs.uk/connecting-party-manager",
        ),
    ],
)
def test_get_base_url_persistent_workspaces(
    workspace: str, environment: str, base_url: str
):
    assert get_base_url(workspace=workspace, environment=environment) == base_url


@pytest.mark.parametrize(
    ["workspace", "environment", "base_url"],
    [
        (
            "foobar",
            "dev",
            "https://internal-dev.api.service.nhs.uk/foobar",
        ),
        (
            "foobar-sandbox",
            "dev",
            "https://internal-dev.api.service.nhs.uk/foobar-sandbox",
        ),
        (
            "foobar",
            "qa",
            "https://internal-qa.api.service.nhs.uk/foobar",
        ),
        (
            "foobar-sandbox",
            "qa",
            "https://internal-qa.api.service.nhs.uk/foobar-sandbox",
        ),
    ],
)
def test_get_base_url_temporary_workspaces(
    workspace: str, environment: str, base_url: str
):
    """Tests that none of the above go to a sandbox deployment, even if they contain 'sandbox'"""
    assert get_base_url(workspace=workspace, environment=environment) == base_url
