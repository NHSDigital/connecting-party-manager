import pytest


def pytest_runtest_logreport(report):
    if report.when == "call" and report.passed and hasattr(pytest, "success_message"):
        # Print the success message in green
        print(f"\n\033[92m{pytest.success_message} .\033[0m")  # noqa: T201
