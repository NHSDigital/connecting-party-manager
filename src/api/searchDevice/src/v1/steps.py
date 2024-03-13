from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from event.step_chain import StepChain

from ..data.response import devices, endpoints


def get_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["device_type"]
    return {"product": devices, "endpoint": endpoints}.get(device_type.lower(), {})


steps = [
    get_results,
]
