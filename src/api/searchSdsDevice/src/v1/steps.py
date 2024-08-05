from typing import List

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.query import SearchSDSDeviceQueryParams
from domain.core.device import Device
from domain.repository.device_repository.v2 import DeviceRepository
from domain.response.validation_errors import InboundValidationError
from event.step_chain import StepChain
from pydantic import ValidationError


def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = event.query_string_parameters
    try:
        search_query_params = SearchSDSDeviceQueryParams(**query_params)
        params = search_query_params.get_non_null_params()
        return {
            "query_string": params,
            "host": event.multi_value_headers["Host"],
        }
    except ValidationError as exc:
        raise InboundValidationError(
            errors=exc.raw_errors,
            model=exc.model,
        )


def query_devices(data, cache) -> List[Device]:
    event_data = data[parse_event_query]
    query_params = event_data.get("query_string")
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = device_repo.query_by_tag_mock(**query_params)
    return results


steps = [
    parse_event_query,
    query_devices,
]
