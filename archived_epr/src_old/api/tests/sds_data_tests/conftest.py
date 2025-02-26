import json
import subprocess

import pytest

current_file_index = 0
entry_count = 0
max_entries_per_file = 2000
file_name_template = "src/api/tests/sds_data_tests/test_success_{}.json"


@pytest.fixture(scope="session", autouse=True)
def run_after_tests():
    # This code will run after all tests have finished
    yield
    # Code to run after tests
    subprocess.run(
        ["python", "src/api/tests/sds_data_tests/calculation.py"], check=True
    )


def get_current_file():
    """Helper function to get the current file name."""
    global current_file_index
    return file_name_template.format(current_file_index)


def strip_request_from_message(message):
    # Find the index of ", request = " and slice the string
    split_index = message.find(", request = ")
    if split_index != -1:
        beginning = message[:split_index]

        # Extract the part of the message after ", request = "
        removed_message = message[split_index + len(", request = ") :]

        # Split the removed message into lines
        lines = removed_message.splitlines()

        # Get the last two lines (if there are at least two lines)
        last_two_lines = lines[-4:] if len(lines) >= 4 else lines

        return beginning, last_two_lines
    return message, []


def pytest_runtest_logreport(report):
    global current_file_index, entry_count, max_entries_per_file

    if report.when == "call" and report.failed:
        failed_request, assertion_error = strip_request_from_message(
            str(report.longreprtext)
        )
        output = {"failed_request": failed_request, "error": assertion_error}
        with open("src/api/tests/sds_data_tests/test_failure.json", "a") as f:
            f.write(json.dumps(output))
            f.write(",")
    if report.when == "call" and report.passed and hasattr(pytest, "success_message"):
        # Print the success message in green
        print(f"\n\033[92m{pytest.success_message} .\033[0m")  # noqa: T201
    if (
        report.when == "call"
        and report.passed
        and hasattr(pytest, "success_message_full")
    ):
        # Check if the current file has reached the maximum number of entries
        if entry_count >= max_entries_per_file:
            current_file_index += 1  # Move to the next file
            entry_count = 0  # Reset entry count for the new file

        # Write to the current file
        with open(get_current_file(), "a") as f:
            f.write(pytest.success_message_full)
            f.write("\n")  # Optionally add a newline after each entry

        entry_count += 1  # Increment the entry count
