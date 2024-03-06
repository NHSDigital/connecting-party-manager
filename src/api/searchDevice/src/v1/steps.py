import os

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from event.step_chain import StepChain

def get_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["type"]
    dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), os.path.join("tests", "test_data", "endpoints_response.json"))
    if device_type.lower() == "product":
        dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), os.path.join("tests", "test_data", "devices_response.json"))
    with open(dir_path, 'r') as f:
        return json.load(f)

steps = [
    get_results,
]
