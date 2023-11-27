from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team import ProductTeam
from event.step_chain import StepChain


def _read_product_team(event: APIGatewayProxyEvent) -> ProductTeam:
    id = event.path_parameters["id"]
    return f"ProductTeam({id})"  # Replace this with the result from the DB


def read_product_team(data, cache) -> ProductTeam:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return _read_product_team(event=event)


steps = [
    read_product_team,
]
