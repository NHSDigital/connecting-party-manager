import os

import pytest

from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test_read_my_test_model_not_exists():
    os.environ["DYNAMODB_TABLE"] = read_terraform_output("dynamodb_table_name.value")
    from .repository_test_utils import _test_read_my_test_model_mock_not_exists

    _test_read_my_test_model_mock_not_exists(create_table=False)


@pytest.mark.integration
def test_read_write_my_test_model():
    os.environ["DYNAMODB_TABLE"] = read_terraform_output("dynamodb_table_name.value")
    from .repository_test_utils import _test_read_write_my_test_model_mock

    _test_read_write_my_test_model_mock(create_table=False)
