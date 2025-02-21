import ast
import glob
import json
import math
import os
import statistics

from event.json import json_loads


def preprocess_json_file(file_path):
    with open(file_path, "r") as f:
        content = f.read().strip()
        # Add brackets around the content to form a valid JSON array
        content = f"[{content}]"

        # Replace ',{' with '},{' to ensure proper JSON array formatting
        content = content.replace("},{", "},{")

        # Remove any trailing commas (`,]` is not valid JSON)
        content = content.replace(",]", "]")

        try:
            data = json_loads(content)  # noqa: T201
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in file {file_path}: {e}")  # noqa: T201
            raise
    return data


def transform_params(params_str):
    # Convert the string representation of the dictionary to an actual dictionary
    try:
        params_dict = ast.literal_eval(params_str)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing string to dictionary: {e}")  # noqa: T201
        return {}

    # Transform the dictionary, excluding "use_cpm"
    transformed_dict = {
        f"request.params.{key}": value
        for key, value in params_dict.items()
        if key != "use_cpm"  # Ignore the "use_cpm" key
    }

    return transformed_dict


def extract_response_times(json_files):
    ldap_times = []
    cpm_times = []
    params = []

    for file in json_files:
        data = preprocess_json_file(file)
        for entry in data:
            ldap_times.append(entry["ldap_response_time"])
            cpm_times.append(entry["cpm_response_time"])
            params_dict = transform_params(entry["params"])
            params_dict["path"] = entry["path"]
            params.append(params_dict)

    return ldap_times, cpm_times, params


def format_value(value):
    return f"{value:.2f} ms"


def calculate_statistics(times_list):
    if not times_list:
        return {
            "mean": "0.00 ms",
            "mean_under_1s": "0.00 ms",
            "mode": "N/A",
            "lowest": "0.00 ms",
            "highest": "0.00 ms",
            "median": "0.00 ms",
        }

    try:
        mode_value = statistics.mode(times_list)
    except statistics.StatisticsError:
        mode_value = "N/A"  # No unique mode found

    geometric_mean = math.exp(sum(math.log(x) for x in times_list) / len(times_list))

    # Filter times under 1000ms
    times_under_1s = [time for time in times_list if time < 1000]

    mean_under_1s = sum(times_under_1s) / len(times_under_1s) if times_under_1s else 0

    return {
        "mean": format_value(sum(times_list) / len(times_list)),
        "mean_under_1s": format_value(mean_under_1s),
        "mode": format_value(mode_value) if mode_value != "N/A" else mode_value,
        "lowest": format_value(min(times_list)),
        "highest": format_value(max(times_list)),
        "median": format_value(statistics.median(times_list)),
    }


def write_to_json_file(output_file_path, data_list):
    # Check if the file already exists
    if os.path.exists(output_file_path):
        print(  # noqa: T201
            f"The file '{output_file_path}' already exists. No action will be taken."  # noqa: T201
        )  # noqa: T201
        return

    # Write the list to the JSON file if it does not exist
    with open(output_file_path, "w") as file:
        json.dump(data_list, file, indent=4)


# Get all JSON files in the directory
# json_files = ["test_success_0.json", "test_success_1.json", "test_success_2.json"]
json_files = glob.glob("src/api/tests/sds_data_tests/test_success_*.json")
# json_files = glob.glob("*.json")

# Extract response times
ldap_times, cpm_times, params = extract_response_times(json_files)
output_file_path = (
    "src/api/tests/sds_data_tests/data/sds_fhir_api.speed_test_queries.device.json"
)

# Calculate statistics
ldap_stats = calculate_statistics(ldap_times)
cpm_stats = calculate_statistics(cpm_times)

print(f"LDAP Response Time Stats: {ldap_stats}")  # noqa: T201
print(f"CPM Response Time Stats: {cpm_stats}")  # noqa: T201
write_to_json_file(output_file_path, params)
