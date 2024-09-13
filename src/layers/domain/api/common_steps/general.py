from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.response.validation_errors import mark_json_decode_errors_as_inbound
from event.step_chain import StepChain


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}
