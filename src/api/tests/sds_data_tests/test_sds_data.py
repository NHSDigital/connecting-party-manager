import os
import random

import requests
from event.json import json_load

# import pytest

# @pytest.mark.smoke


def _request(request):
    url = "https://api.service.nhs.uk/spine-directory/FHIR/R4/"
    res = requests.get(url, params=request["params"])
    return res.status_code, res.json()


def test_api_responses_match():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data", "sds_fhir_api.unique_queries.json")
    with open(file_path, "r") as file:
        data = json_load(file)

    transformed_data = []
    for item in data:
        transformed_item = {"params": {}, "path": item.get("path")}

        for key, value in item.items():
            if ".params." in key:
                # Extract the actual param name by splitting the key
                param_name = key.split(".params.")[-1]
                transformed_item["params"][param_name] = value
            elif key == "path":
                # Path key remains as is
                transformed_item["path"] = value
        transformed_data.append(transformed_item)
    test_items = random.sample(transformed_data, 5)
    for item in test_items:
        ldap_status, ldap_body = _request(item)
        cpm_item = item
        cpm_item["params"]["use_cpm"] = "iwanttogetdatafromcpm"
        cpm_status, cpm_body = _request(cpm_item)
        assert ldap_status == cpm_status
        if ldap_status == 404:
            # assert ldap_body['issue'][0]['diagnostics'] == cpm_body['issue'][0]['diagnostics']
            pass
        else:
            pass
