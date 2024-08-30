import json

import pytest


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
    if report.when == "call" and report.failed:
        failed_request, assertion_error = strip_request_from_message(
            str(report.longreprtext)
        )
        output = {"failed_request": failed_request, "error": assertion_error}
        with open("test_failure.json", "a") as f:
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
        with open("test_success.json", "a") as f:
            f.write(pytest.success_message_full)
