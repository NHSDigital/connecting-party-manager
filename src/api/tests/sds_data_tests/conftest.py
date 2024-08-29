import json

import pytest


def strip_request_from_message(message):
    # Find the index of ", request = " and slice the string
    split_index = message.find(", request = ")
    if split_index != -1:
        return message[:split_index]
    return message


def pytest_runtest_logreport(report):
    if report.when == "call" and report.failed:
        output = {
            "failed_request": strip_request_from_message(str(report.longreprtext))
        }
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
