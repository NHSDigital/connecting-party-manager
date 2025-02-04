from collections import defaultdict
from pathlib import Path

from botocore.config import Config
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team_epr.v1 import ProductTeam
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.epr_product_repository.v1 import EprProductRepository
from domain.repository.product_team_epr_repository.v1 import ProductTeamRepository

# Configure the boto3 retry settings
config = Config(retries={"max_attempts": 10, "mode": "standard"})

PATH_TO_STAGE_DATA = Path(__file__).parent / "stage_data"


def _nested_dict():
    return defaultdict(_nested_dict)


def _undefault_nested_dict(nested_dict: dict):
    return {
        k: _undefault_nested_dict(v) if isinstance(v, dict) else v
        for k, v in nested_dict.items()
    }


def aggregate_database(table_name, dynamodb_client):
    product_team_repo = ProductTeamRepository(
        table_name=table_name, dynamodb_client=dynamodb_client
    )
    product_repo = EprProductRepository(
        table_name=table_name, dynamodb_client=dynamodb_client
    )
    device_repo = DeviceRepository(
        table_name=table_name, dynamodb_client=dynamodb_client
    )
    device_ref_data_repo = DeviceReferenceDataRepository(
        table_name=table_name, dynamodb_client=dynamodb_client
    )

    nested_dict = lambda: defaultdict(nested_dict)
    aggregated_data = nested_dict()
    for product_team in product_team_repo.search():
        (product_team_key,) = product_team.keys
        _product_team_data = aggregated_data[ProductTeam][product_team_key.key_value]

        for product in product_repo.search(product_team_id=product_team.id):
            (product_key,) = product.keys
            _product_data = _product_team_data[EprProduct][product_key.key_value]

            _product_data[Device] = sorted(
                device.name
                for device in device_repo.search(
                    product_team_id=product_team.id,
                    product_id=product.id,
                    environment=Environment.PROD,
                )
            )

            _product_data[DeviceReferenceData] = sorted(
                device_ref_data.name
                for device_ref_data in device_ref_data_repo.search(
                    product_team_id=product_team.id,
                    product_id=product.id,
                    environment=Environment.PROD,
                )
            )

    return _undefault_nested_dict(aggregated_data)


# @pytest.mark.integration
# def test_update_without_trigger():
#     new_changelog_number = 123
#     etl_config = get_etl_config(f"{new_changelog_number}.ldif")
#     state_machine_input = StateMachineInput.update(
#         changelog_number_start=0, changelog_number_end=new_changelog_number
#     )
#     step_functions_client = boto3.client("stepfunctions", config=config)
#     s3_client = boto3.client("s3")
#     db_client = dynamodb_client()  # noqa

#     # Clean state
#     clear_etl_state(s3_client=s3_client, etl_config=etl_config)
#     initial_aggregated_data = aggregate_database(
#         table_name=etl_config.table_name, dynamodb_client=db_client
#     )
#     assert initial_aggregated_data == {}

#     # Initial state
#     input_data = []
#     for path in sorted(map(str, PATH_TO_STAGE_DATA.glob("0.extract_input.*.ldif"))):
#         with open(path) as f:
#             input_data.append(f.read())

#     s3_client.put_object(
#         Bucket=etl_config.bucket,
#         Key=WorkerKey.EXTRACT,
#         Body=LDIF_RECORD_DELIMITER.join(input_data),
#     )

#     # Execute
#     execute_state_machine(
#         state_machine_input=state_machine_input,
#         step_functions_client=step_functions_client,
#     )

#     # Final state
#     assert was_changelog_number_updated(
#         s3_client=s3_client,
#         bucket=etl_config.bucket,
#         new_changelog_number=new_changelog_number,
#     )
#     assert extract_is_empty(s3_client=s3_client, bucket=etl_config.bucket)
#     assert transform_is_empty(s3_client=s3_client, bucket=etl_config.bucket)
#     assert load_is_empty(s3_client=s3_client, bucket=etl_config.bucket)

#     final_aggregated_data = aggregate_database(
#         table_name=etl_config.table_name, dynamodb_client=db_client
#     )
#     assert final_aggregated_data == {
#         ProductTeam: {
#             "EPR-LSP04": {
#                 CpmProduct: {
#                     "AAA-111111": {
#                         Device: ["AAA-111111 - Message Handling System"],
#                         DeviceReferenceData: ["AAA-111111 - MHS Message Sets"],
#                     },
#                     "BBB-111111": {
#                         Device: ["BBB-111111 - Message Handling System"],
#                         DeviceReferenceData: ["BBB-111111 - MHS Message Sets"],
#                     },
#                 },
#             },
#         },
#     }
