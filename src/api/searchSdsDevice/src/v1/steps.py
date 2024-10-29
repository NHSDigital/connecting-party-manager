from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.sds.query import SearchSDSDeviceQueryParams
from domain.repository.device_repository.v2 import DeviceRepository
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def _parse_event_query(query_params: dict):
    search_query_params = SearchSDSDeviceQueryParams(**query_params)
    return search_query_params.get_non_null_params()


def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = _parse_event_query(event.query_string_parameters or {})
    return {
        "query_params": query_params,
        "host": event.multi_value_headers["Host"],
    }


def query_devices(data, cache) -> dict:
    event_data: dict = data[parse_event_query]
    query_params: dict = event_data.get("query_params")
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = device_repo.query_by_tag(**query_params)
    return HTTPStatus.OK, [result.state() for result in results]


steps = [
    parse_event_query,
    query_devices,
]
