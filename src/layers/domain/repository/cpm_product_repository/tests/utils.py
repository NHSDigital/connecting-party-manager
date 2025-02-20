from collections.abc import Generator

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.dynamodb import mock_table_cpm
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my_table"


def repository_fixture_cpm[
    T
](is_integration_test: bool, repository_class: type[T]) -> Generator[T, None, None]:
    if is_integration_test:
        table_name = read_terraform_output("dynamodb_cpm_table_name.value")
        client = dynamodb_client()
        yield repository_class(table_name=table_name, dynamodb_client=client)
    else:
        with mock_table_cpm(TABLE_NAME) as client:
            yield repository_class(table_name=TABLE_NAME, dynamodb_client=client)
