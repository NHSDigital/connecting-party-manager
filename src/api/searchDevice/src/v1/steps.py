from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from event.step_chain import StepChain
from searchDevice.src.data.response import devices, endpoints


def get_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["device_type"]
    if device_type.lower() == "product":
        return devices
    elif device_type.lower() == "endpoint":
        return endpoints

    return {}


steps = [
    get_results,
]
