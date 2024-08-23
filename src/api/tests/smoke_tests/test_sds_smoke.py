import os

import pytest
import requests

from test_helpers.terraform import read_terraform_output

from .utils import get_app_key, get_base_url


def _request(request):
    url = f"{request['domain']}/spine-directory/FHIR/R4{request['path']}"
    res = requests.get(url, params=request["params"], headers=request["headers"])
    return res.status_code


@pytest.mark.smoke
def test_sds_smoke_tests():
    workspace = os.environ.get("WORKSPACE") or read_terraform_output("workspace.value")
    environment = os.environ.get("ACCOUNT") or read_terraform_output(
        "environment.value"
    )
    domain_cpm = get_base_url(workspace=workspace, environment=environment)
    pos = domain_cpm.rfind("/")
    domain = domain_cpm[:pos]
    request = {
        "path": "/Device",
        "params": {
            "identifier": "https%3A%2F%2Ffhir.nhs.uk%2FId%2FnhsServiceInteractionId%7Curn%3Anhs%3Anames%3Aservices%3Apsisquery%3AFOO",
            "organization": "https%3A%2F%2Ffhir.nhs.uk%2FId%2Fods-organization-code%7CBAR",
        },
        "domain": domain,
        "headers": {"apikey": get_app_key(environment=environment, project="-sds")},
    }
    status_code = _request(request=request)
    assert status_code == 200
