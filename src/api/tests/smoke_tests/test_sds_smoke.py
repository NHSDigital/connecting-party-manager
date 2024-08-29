import os

import pytest
import requests

from test_helpers.terraform import read_terraform_output

from .utils import get_app_key, get_base_url


def _request(request):
    url = f"{request['domain']}/spine-directory/FHIR/R4{request['path']}"
    res = requests.get(url, params=request["params"], headers=request["headers"])
    return res.status_code, res.json()


@pytest.mark.parametrize(
    "apirequest",
    [
        {
            "path": "/Device",
            "params": {
                "identifier": "https://fhir.nhs.uk/Id/nhsServiceInteractionId|FOO",
                "organization": "https://fhir.nhs.uk/Id/ods-organization-code|BAR",
                "use_cpm": "iwanttogetdatafromcpm",
            },
        },
        {
            "path": "/Endpoint",
            "params": {
                "identifier": "https://fhir.nhs.uk/Id/nhsServiceInteractionId|FOO",
                "organization": "https://fhir.nhs.uk/Id/ods-organization-code|BAR",
                "use_cpm": "iwanttogetdatafromcpm",
            },
        },
    ],
)
@pytest.mark.smoke
def test_sds_smoke_tests(apirequest):
    workspace = os.environ.get("WORKSPACE") or read_terraform_output("workspace.value")
    environment = os.environ.get("ACCOUNT") or read_terraform_output(
        "environment.value"
    )
    domain_cpm = get_base_url(workspace=workspace, environment=environment)
    pos = domain_cpm.rfind("/")
    domain = domain_cpm[:pos]
    apirequest["domain"] = domain
    apirequest["headers"] = {
        "apikey": get_app_key(environment=environment, project="-sds")
    }
    status_code, _ = _request(request=apirequest)
    assert status_code == 200
