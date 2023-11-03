from types import FunctionType

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel


def validate_event(data, cache):
    return APIGatewayProxyEventModel(**data["event"])


event_processing_steps: list[FunctionType] = [
    validate_event,
]
