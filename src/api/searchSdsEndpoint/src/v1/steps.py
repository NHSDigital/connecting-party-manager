from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.sds.query import SearchSDSEndpointQueryParams
from domain.repository.device_repository import DeviceRepository
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def _parse_event_query(query_params: dict):
    search_query_params = SearchSDSEndpointQueryParams(**query_params)
    return search_query_params.get_non_null_params()


def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = _parse_event_query(query_params=event.query_string_parameters or {})

    return {
        "query_params": query_params,
        "host": event.multi_value_headers["Host"],
    }


def sort_query_params(data, cache):
    event_data: dict = data[parse_event_query]
    query_params: dict = event_data.get("query_params")
    if (
        "nhs_id_code" in query_params
        and "nhs_mhs_party_key" in query_params
        and len(query_params)
    ):
        nhs_id_code = query_params.pop("nhs_id_code", None)

    return query_params


def query_endpoints(data, cache) -> list[dict]:
    query_params: dict = data[sort_query_params]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = device_repo.query_by_tag(**query_params)
    return HTTPStatus.OK, [result.state() for result in results]


steps = [
    parse_event_query,
    query_endpoints,
]
