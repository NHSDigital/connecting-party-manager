import pytest
from etl_utils.io import pkl_load_lz4
from event.aws.client import dynamodb_client as get_dynamodb_client
from mypy_boto3_s3 import S3Client
from sds.epr.updates.tests.test_process_request_to_add_mhs import equivalent

from test_helpers.terraform import read_terraform_output

from .conftest import ETL_BUCKET, parametrize_over_scenarios
from .utils import Handler, Scenario, as_domain_object, convert_list_likes, read_all


class EtlError(Exception):
    pass


@parametrize_over_scenarios()
def test_extract(scenario: Scenario, extract_handler: Handler, s3_client: S3Client):
    handler_response = extract_handler(event={}, context=None)
    error_message = handler_response.get("error_message")
    assert not error_message, error_message

    response = s3_client.get_object(
        Bucket=ETL_BUCKET, Key="input--transform/unprocessed"
    )
    actual_extract_output = pkl_load_lz4(response["Body"])
    assert convert_list_likes(actual_extract_output) == convert_list_likes(
        scenario.extract_output
    )


def run_transform_and_load(transform_handler: Handler, load_handler: Handler):
    unprocessed_transform_records = None
    while unprocessed_transform_records is None or unprocessed_transform_records > 0:
        transform_response = transform_handler(
            event={"max_records": 1, "etl_type": "updates"}, context=None
        )
        error_message = transform_response.get("error_message")
        if error_message:
            raise EtlError(error_message)
        unprocessed_transform_records = transform_response.get("unprocessed_records")

        unprocessed_load_records = None
        while unprocessed_load_records is None or unprocessed_load_records > 0:
            load_response = load_handler(
                event={"max_records": 1, "etl_type": "updates"}, context=None
            )
            error_message = load_response.get("error_message")
            if error_message:
                raise EtlError(error_message)
            unprocessed_load_records = load_response.get("unprocessed_records")


@pytest.mark.integration
@parametrize_over_scenarios()
def test_transform_and_load(
    scenario: Scenario, transform_handler: Handler, load_handler: Handler
):
    try:
        run_transform_and_load(
            transform_handler=transform_handler, load_handler=load_handler
        )
    except EtlError as error:
        if not scenario.expected_errors:
            raise
        (expected_error_snippet,) = scenario.expected_errors
        try:
            assert expected_error_snippet in str(error)
        except AssertionError:
            print("Snippet not found in error message, see below diff:")  # noqa: T201
            assert str(error) == expected_error_snippet
        return

    n_expected_errors = len(scenario.expected_errors)
    assert (
        n_expected_errors == 0
    ), f"{n_expected_errors} errors were expected but none were raised"

    dynamodb_client = get_dynamodb_client()
    table_name = read_terraform_output("dynamodb_table_name.value")
    created_objs = list(read_all(table_name=table_name, db_client=dynamodb_client))
    expected_objs = list(map(as_domain_object, scenario.load_output))

    for created_obj in created_objs:
        found_match = False
        expected_objs_with_matching_type = list(
            filter(lambda o: type(o) is type(created_obj), expected_objs)
        )

        failed_assertions = []
        for expected_obj in expected_objs_with_matching_type:
            try:
                assert equivalent(created_obj, expected_obj)
            except AssertionError as error:
                failed_assertions.append(
                    f"{type(expected_obj)}:{expected_obj.id}: {error}"
                )
            else:
                found_match = True
                break

        if not found_match:
            msg = "\n\n".join(failed_assertions)
            raise ValueError(
                f"Could not find match in expected output for {created_obj}. Tried:\n{msg}"
            )
