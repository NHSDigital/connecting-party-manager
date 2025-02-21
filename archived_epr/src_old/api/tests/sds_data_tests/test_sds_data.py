import json
import os
import random
import re
import sys
import time
import urllib.parse
from copy import deepcopy

import pytest
import requests
from event.json import json_load

non_prod_urls = {
    "local": "http://localhost:9000",
    "dev": "https://internal-dev.api.service.nhs.uk/spine-directory/FHIR/R4",
    "qa": "https://internal-qa.api.service.nhs.uk/spine-directory/FHIR/R4",
}


def _create_output_json(
    ldap_status,
    cpm_status,
    ldap_body,
    cpm_body,
    path,
    params,
    ldap_response_time,
    cpm_response_time,
):
    output = {
        "ldap_status": ldap_status,
        "ldap_body": str(ldap_body),
        "cpm_status": cpm_status,
        "cpm_body": str(cpm_body),
        "path": path,
        "params": str(params),
        "ldap_response_time": ldap_response_time,
        "cpm_response_time": cpm_response_time,
    }
    return json.dumps(output)


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


def sort_entries_by_nhsserviceinteractionid_value(entries):
    def get_nhsserviceinteractionid_value(entry):
        # Get the list of extensions for the current entry
        extensions = entry["resource"]["extension"]

        # Iterate through the extensions to find the one with url == "FOOBAR2"
        for ext in extensions:
            if (
                ext["url"]
                == "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-NhsServiceInteractionId"
            ):
                # Return the value associated with this extension
                return ext["valueReference"]["identifier"]["value"]

        # If FOOBAR2 is not found, return an empty string or any fallback value
        return ""

    # Sort the entries using the value from the FOOBAR2 extension
    sorted_entries = sorted(entries, key=get_nhsserviceinteractionid_value)

    return sorted_entries


def sort_entries_by_identifier_value(entries):
    def get_partykey_value(entry):
        identifiers = entry["resource"]["identifier"]
        for idt in identifiers:
            if idt["system"] == "https://fhir.nhs.uk/Id/nhsMhsPartyKey":
                return idt["value"]
        return ""

    sorted_entries = sorted(entries, key=get_partykey_value)
    return sorted_entries


def normalize_case(data):
    """
    Recursively traverse the dictionary and normalize the case of all string keys and values.
    """
    if isinstance(data, dict):
        return {k.lower(): normalize_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_case(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data


def _request_base(url, request, headers):
    retry = 0
    start_time = time.time()
    res = requests.get(url, params=request["params"], headers=headers)
    if res.status_code > 499:
        while res.status_code > 499:
            time.sleep(1)
            start_time = time.time()
            res = requests.get(url, params=request["params"], headers=headers)
            if retry == 3:
                break
            retry += 1
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    return res, response_time


def _request(request):
    apikey = os.getenv("SDS_PROD_APIKEY")
    if not apikey:
        sys.exit(
            "Error: The environment variable 'SDS_PROD_APIKEY' is not set. Please set it and try again."
        )

    url = f"https://api.service.nhs.uk/spine-directory/FHIR/R4{request['path']}"
    headers = {"apiKey": apikey}
    res, response_time = _request_base(url, request, headers)
    return res.status_code, res.json(), response_time


def _request_non_prod(request, url):
    apikey = os.getenv("SDS_DEV_APIKEY")
    if not apikey:
        sys.exit(
            "Error: The environment variable 'SDS_DEV_APIKEY' is not set. Please set it and try again."
        )

    url = f"{url}{request['path']}"
    headers = {"apiKey": apikey}
    res, response_time = _request_base(url, request, headers)
    return res.status_code, res.json(), response_time


def _generate_test_data(filename, test_count=None):
    speed_test = os.getenv("RUN_SPEEDTEST", "FALSE")
    speed_test = speed_test.upper() == "TRUE"
    if speed_test:
        test_count = None
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
                param_value = []
                if isinstance(value, list):
                    for v in value:
                        param_value.append(urllib.parse.unquote(v))
                else:
                    param_value = [urllib.parse.unquote(value)]
                transformed_item["params"][param_name] = param_value
            elif key == "path":
                # Path key remains as is
                transformed_item["path"] = value
        transformed_data.append((transformed_item))
    if not test_count or int(test_count) > len(transformed_data):
        return transformed_data

    return random.sample(transformed_data, int(test_count))


def _assert_response_match(expected, result, item, name):
    assert len(result["entry"]) == len(
        expected["entry"]
    ), f"Entries do not match the total. When calling with {item}"
    if item["path"] == "/Endpoint":
        sorted_entries_result = sort_entries_by_nhsserviceinteractionid_value(
            result["entry"]
        )
        sorted_entries_result = sort_entries_by_identifier_value(sorted_entries_result)
        result["entry"] = sorted_entries_result
        sorted_entries_expected = sort_entries_by_nhsserviceinteractionid_value(
            expected["entry"]
        )
        sorted_entries_expected = sort_entries_by_identifier_value(
            sorted_entries_expected
        )
        expected["entry"] = sorted_entries_expected
    for idx, device_value in enumerate(result["entry"]):
        assert (
            device_value["resource"]["resourceType"]
            == expected["entry"][idx]["resource"]["resourceType"]
        ), f"ResourceTypes do not match. When calling with {item}"
        for index, ext in enumerate(device_value["resource"]["extension"]):
            if "extension" in ext:
                for extension in ext["extension"]:
                    assert normalize_case(extension) in normalize_case(
                        expected["entry"][idx]["resource"]["extension"][index][
                            "extension"
                        ]
                    ), f"Extension not in {name}. When calling with {item}"
        for identifier in device_value["resource"]["identifier"]:
            assert normalize_case(identifier) in normalize_case(
                expected["entry"][idx]["resource"]["identifier"]
            ), f"Identifier not in {name}. When calling with {item}"
        if item["path"] != "/Endpoint":
            assert (
                "owner" in device_value["resource"]
            ), f"Key 'owner' does not exist in the device. When calling with {item}"
            assert (
                device_value["resource"]["owner"]
                == expected["entry"][idx]["resource"]["owner"]
            ), f"Owners do not match. When calling with {item}"
        else:
            assert (
                device_value["resource"]["managingOrganization"]
                == expected["entry"][idx]["resource"]["managingOrganization"]
            )
            assert (
                device_value["resource"]["address"]
                == expected["entry"][idx]["resource"]["address"]
            )


speed_test = os.getenv("RUN_SPEEDTEST", "FALSE")
speed_test = speed_test.upper() == "TRUE"
if not speed_test:
    unique_data = (
        _generate_test_data(
            "sds_fhir_api.failed_queries.device.json",
            test_count=os.getenv("TEST_COUNT", None),
        )
        + _generate_test_data(
            "sds_fhir_api.unique_queries.device.json",
            test_count=os.getenv("TEST_COUNT", None),
        )
        + _generate_test_data(
            "sds_fhir_api.unique_queries.endpoint.json",
            test_count=os.getenv("TEST_COUNT", None),
        )
    )
else:
    unique_data = _generate_test_data(
        "sds_fhir_api.speed_test_queries.device.json",
        test_count=os.getenv("TEST_COUNT", None),
    )


@pytest.mark.parametrize(
    "item",
    unique_data,
)
@pytest.mark.matrix
def test_api_responses_match(item, request):
    ldap_status, ldap_body, ldap_response_time = _request(item)
    if ldap_status < 500:
        use_cpm_prod = os.getenv("USE_CPM_PROD", "FALSE")
        use_cpm_prod = use_cpm_prod.upper() == "TRUE"
        cpm_item = item
        cpm_item["params"]["use_cpm"] = "iwanttogetdatafromcpm"
        retry_cpm = 0
        if use_cpm_prod:
            cpm_status, cpm_body, cpm_response_time = _request(cpm_item)
        else:
            non_prod_env = os.getenv("COMPARISON_ENV", "local")
            cpm_status, cpm_body, cpm_response_time = _request_non_prod(
                cpm_item, non_prod_urls[non_prod_env]
            )

        if cpm_status < 500:
            # Check if 429.
            if cpm_status == 429:
                assert False, f"CPM responded with {cpm_status} for {item}"
            if ldap_status != 200:
                assert (
                    cpm_status == ldap_status
                ), f"Status do not match. When calling with {item}"
                assert (
                    ldap_body["issue"][0]["diagnostics"]
                    == cpm_body["issue"][0]["diagnostics"]
                ), f"Non 200 diagnositc message does not match. When calling with {item}"
                pytest.success_message = f"Response Status of {ldap_status} match / Diagnostic messages match: {ldap_body['issue'][0]['diagnostics']} / Response time: LDAP, CPM / {ldap_response_time:.2f}ms, {cpm_response_time:.2f}ms"
                pytest.success_message_full = f"{_create_output_json(ldap_status, cpm_status, ldap_body, cpm_body, item['path'], item['params'], ldap_response_time, cpm_response_time)},"
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
                        expected=ldap_body_reordered,
                        result=cpm_body_reordered,
                        item=item,
                        name="CPM",
                    )
                    _assert_response_match(
                        expected=cpm_body_reordered,
                        result=ldap_body_reordered,
                        item=item,
                        name="LDAP",
                    )
                    pytest.success_message = f"Response Status of {ldap_status} match / Responses both contain {ldap_body_reordered['total']} devices and all devices are present in both responses / Response time: LDAP, CPM / {ldap_response_time:.2f}ms, {cpm_response_time:.2f}ms"
                    pytest.success_message_full = f"{_create_output_json(ldap_status, cpm_status, ldap_body_reordered, cpm_body_reordered, item['path'], item['params'], ldap_response_time, cpm_response_time)},"
                else:
                    if ldap_body_reordered["total"] == cpm_body_reordered["total"]:
                        assert len(cpm_body_reordered["entry"]) == len(
                            ldap_body_reordered["entry"]
                        ), f"Entries do not match the total. When calling with {item}"
                        _assert_response_match(
                            expected=ldap_body_reordered,
                            result=cpm_body_reordered,
                            item=item,
                            name="CPM",
                        )
                        _assert_response_match(
                            expected=cpm_body_reordered,
                            result=ldap_body_reordered,
                            item=item,
                            name="LDAP",
                        )
                        pytest.success_message = f"Response Status of {ldap_status} match / Responses both contain {ldap_body_reordered['total']} devices and all devices are present in both responses / Response time: LDAP, CPM / {ldap_response_time:.2f}ms, {cpm_response_time:.2f}ms"
                        pytest.success_message_full = f"{_create_output_json(ldap_status, cpm_status, ldap_body_reordered, cpm_body_reordered, item['path'], item['params'], ldap_response_time, cpm_response_time)},"
                    else:
                        assert len(cpm_body_reordered["entry"]) == len(
                            ldap_body_reordered["entry"]
                        ), f"Entries do not match the total. When calling with {item}"

            test_count = os.getenv("TEST_COUNT", None)
            if not test_count:
                time.sleep(0.5)

        else:
            assert False, f"CPM responded with a {cpm_status} error with {item}"

    else:
        assert False, f"LDAP responded with a {ldap_status} error with {item}"


@pytest.mark.parametrize(
    "item",
    _generate_test_data("sds_fhir_queries_errors.json"),
)
@pytest.mark.matrix
def test_api_responses_expected_errors(item):
    if not speed_test:
        ldap_status, ldap_body, ldap_response_time = _request(item)
        use_cpm_prod = os.getenv("USE_CPM_PROD", "FALSE")
        use_cpm_prod = use_cpm_prod.upper() == "TRUE"
        cpm_item = item
        cpm_item["params"]["use_cpm"] = "iwanttogetdatafromcpm"
        if use_cpm_prod:
            cpm_status, cpm_body, cpm_response_time = _request(cpm_item)
        else:
            non_prod_env = os.getenv("COMPARISON_ENV", "local")
            cpm_status, cpm_body, cpm_response_time = _request_non_prod(
                cpm_item, non_prod_urls[non_prod_env]
            )

        assert (
            cpm_status == ldap_status
        ), f"Status do not match. When calling with {item}"
        if ldap_status != 200:
            assert (
                ldap_body["issue"][0]["diagnostics"]
                == cpm_body["issue"][0]["diagnostics"]
            ), f"Non 200 diagnostic message does not match. When calling with {item}"
            pytest.success_message = f"Response Status of {ldap_status} match / Diagnostic messages match: {ldap_body['issue'][0]['diagnostics']} / Response time: LDAP, CPM / {ldap_response_time:.2f}ms, {cpm_response_time:.2f}ms"
            pytest.success_message_full = f"{_create_output_json(ldap_status, cpm_status, ldap_body, cpm_body, item['path'], item['params'], ldap_response_time, cpm_response_time)},"
        else:
            assert ldap_body["entry"] == cpm_body["entry"]
