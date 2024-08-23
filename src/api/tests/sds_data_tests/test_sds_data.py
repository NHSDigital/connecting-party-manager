import os
import random
import re
import sys
import urllib.parse
from copy import deepcopy

import pytest
import requests
from event.json import json_load


def clean_json(data):
    """
    Recursively traverse the JSON-like structure and:
    1. Replace any UUIDs with 'UUID_PLACEHOLDER'.
    2. Replace any string containing 'http://foo' or 'https://bar' with 'FULL_URL'.
    """
    if isinstance(data, dict):
        # Check if the key is 'identifier' and normalize it
        for k, v in data.items():
            if k == "identifier" and isinstance(v, list):
                data[k] = normalize_identifiers(v)
            else:
                data[k] = clean_json(v)
        return data
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
    elif isinstance(data, str):
        data = replace_full_url(data)  # Replace URLs first
        return remove_uuid_from_string(data)  # Then remove UUIDs
    else:
        return data


def normalize_identifiers(identifiers):
    """
    Sorts the list of dictionaries by the 'system' and 'value' keys to ensure order-independent comparison.
    """
    return sorted(identifiers, key=lambda x: (x["system"], x["value"]))


def remove_uuid_from_string(value):
    """
    Replace any UUID found in a string with a placeholder.
    """
    uuid_regex = re.compile(
        r"[a-fA-F0-9]{8}\b-[a-fA-F0-9]{4}\b-[a-fA-F0-9]{4}\b-[a-fA-F0-9]{4}\b-[a-fA-F0-9]{12}"
    )
    return uuid_regex.sub("UUID_PLACEHOLDER", value)


def replace_full_url(value):
    """
    Replace the entire string with 'FULL_URL' if it contains 'https://prod.apis' or 'https://internal-dev'.
    """
    if "prod.apis" in value or "internal-dev" in value:
        return "FULL_URL"
    return value


def get_asid_value(entry):
    """
    Extract the numeric value associated with 'system': 'asid' from the entry.
    If 'system': 'asid' is not found, return a large number to push it to the end.
    """
    for identifier in entry["resource"]["identifier"]:
        if identifier["system"] == "https://fhir.nhs.uk/Id/nhsSpineASID":
            return int(identifier["value"])
    return float("inf")  # If 'asid' is not found, push this entry to the end


def reorder_entries_by_asid_value(data):
    """
    Reorder the 'entry' list in the JSON object based on the numeric 'value' where 'system': 'asid'.
    """
    data["entry"].sort(key=get_asid_value)
    return data


def normalize_case(data):
    """
    Recursively traverse the dictionary and normalize the case of all string keys and values.
    """
    if isinstance(data, dict):
        return {
            k.lower(): normalize_case(v) if isinstance(k, str) else normalize_case(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [normalize_case(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data


def _request(request):
    apikey = os.getenv("SDS_PROD_APIKEY")
    if not apikey:
        sys.exit(
            "Error: The environment variable 'SDS_PROD_APIKEY' is not set. Please set it and try again."
        )

    url = f"https://api.service.nhs.uk/spine-directory/FHIR/R4{request['path']}"
    res = requests.get(url, params=request["params"], headers={"apiKey": apikey})
    return res.status_code, res.json()


def _request_dev(request):
    apikey = os.getenv("SDS_DEV_APIKEY")
    if not apikey:
        sys.exit(
            "Error: The environment variable 'SDS_DEV_APIKEY' is not set. Please set it and try again."
        )

    url = f"https://internal-dev.api.service.nhs.uk/spine-directory/FHIR/R4{request['path']}"
    res = requests.get(url, params=request["params"], headers={"apiKey": apikey})
    return res.status_code, res.json()


def _generate_test_data(filename, test_count=1):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data", filename)
    with open(file_path, "r") as file:
        data = json_load(file)

    transformed_data = []
    for item in data:
        transformed_item = {"params": {}, "path": item.get("path")}

        for key, value in item.items():
            if ".params." in key:
                # Extract the actual param name by splitting the key
                param_name = key.split(".params.")[-1]
                transformed_item["params"][param_name] = urllib.parse.unquote(value)
            elif key == "path":
                # Path key remains as is
                transformed_item["path"] = value
        transformed_data.append((transformed_item))
    test_items = random.sample(transformed_data, test_count)
    return test_items


def _assert_response_match(ldap_body_reordered, cpm_body_reordered, item):
    assert len(cpm_body_reordered["entry"]) == len(
        ldap_body_reordered["entry"]
    ), f"Entries do not match the total. When calling with {item}"
    for idx, device_value in enumerate(cpm_body_reordered["entry"]):
        assert (
            device_value["resource"]["resourceType"]
            == ldap_body_reordered["entry"][idx]["resource"]["resourceType"]
        ), f"ResourceTypes do not match. When calling with {item}"
        for extension in device_value["resource"]["extension"]:
            assert normalize_case(extension) in normalize_case(
                ldap_body_reordered["entry"][idx]["resource"]["extension"]
            ), f"Extension not in LDAP. When calling with {item}"
        for identifier in device_value["resource"]["identifier"]:
            assert normalize_case(identifier) in normalize_case(
                ldap_body_reordered["entry"][idx]["resource"]["identifier"]
            ), f"Identifier not in LDAP. When calling with {item}"
        if item["path"] != "/Endpoint":
            assert (
                "owner" in device_value["resource"]
            ), f"Key 'owner' does not exist in the device. When calling with {item}"
            assert (
                device_value["resource"]["owner"]
                == ldap_body_reordered["entry"][idx]["resource"]["owner"]
            ), f"Owners do not match. When calling with {item}"
        else:
            assert (
                device_value["resource"]["managingOrganization"]
                == ldap_body_reordered["entry"][idx]["resource"]["managingOrganization"]
            )
            assert (
                device_value["resource"]["address"]
                == ldap_body_reordered["entry"][idx]["resource"]["address"]
            )


@pytest.mark.parametrize(
    "item",
    _generate_test_data(
        "sds_fhir_api.unique_queries.json",
        test_count=int(os.getenv("TEST_COUNT", "10")),
    ),
)
@pytest.mark.matrix
def test_api_responses_match(item):
    ldap_status, ldap_body = _request(item)
    use_cpm_prod = os.getenv("USE_CPM_PROD", "FALSE")
    use_cpm_prod = use_cpm_prod.upper() == "TRUE"
    if use_cpm_prod:
        cpm_item = item
        cpm_item["params"]["use_cpm"] = "iwanttogetdatafromcpm"
        cpm_status, cpm_body = _request(cpm_item)
    else:
        cpm_status, cpm_body = _request_dev(item)
    if ldap_status != 200:
        assert (
            cpm_status == ldap_status
        ), f"Status do not match. When calling with {item}"
        assert (
            ldap_body["issue"][0]["diagnostics"] == cpm_body["issue"][0]["diagnostics"]
        ), f"Non 200 diagnositc message does not match. When calling with {item}"
    else:
        assert (
            ldap_status == cpm_status
        ), f"CPM status does not match 200 from ldap. When calling with {item}"
        ldap_body_cleaned = clean_json(deepcopy(ldap_body))
        cpm_body_cleaned = clean_json(deepcopy(cpm_body))
        ldap_body_reordered = reorder_entries_by_asid_value(ldap_body_cleaned)
        cpm_body_reordered = reorder_entries_by_asid_value(cpm_body_cleaned)

        if use_cpm_prod:
            assert ldap_body_reordered["total"] == cpm_body_reordered["total"]
            _assert_response_match(
                ldap_body_reordered=ldap_body_reordered,
                cpm_body_reordered=cpm_body_reordered,
                item=item,
            )
        else:
            if ldap_body_reordered["total"] == cpm_body_reordered["total"]:
                assert len(cpm_body_reordered["entry"]) == len(
                    ldap_body_reordered["entry"]
                ), f"Entries do not match the total. When calling with {item}"
                _assert_response_match(
                    ldap_body_reordered=ldap_body_reordered,
                    cpm_body_reordered=cpm_body_reordered,
                    item=item,
                )
            else:
                assert len(cpm_body_reordered["entry"]) == len(
                    ldap_body_reordered["entry"]
                ), f"Entries do not match the total. When calling with {item}"


@pytest.mark.parametrize(
    "item", _generate_test_data("sds_fhir_queries_errors.json", test_count=6)
)
@pytest.mark.matrix
def test_api_responses_expected_errors(item):
    ldap_status, ldap_body = _request(item)
    use_cpm_prod = os.getenv("USE_CPM_PROD", "FALSE")
    use_cpm_prod = use_cpm_prod.upper() == "TRUE"
    if use_cpm_prod:
        cpm_item = item
        cpm_item["params"]["use_cpm"] = "iwanttogetdatafromcpm"
        cpm_status, cpm_body = _request(cpm_item)
    else:
        cpm_status, cpm_body = _request_dev(item)

    assert cpm_status == ldap_status, f"Status do not match. When calling with {item}"
    if ldap_status != 200:
        assert (
            ldap_body["issue"][0]["diagnostics"] == cpm_body["issue"][0]["diagnostics"]
        ), f"Non 200 diagnositc message does not match. When calling with {item}"
    else:
        assert ldap_body["entry"] == cpm_body["entry"]
