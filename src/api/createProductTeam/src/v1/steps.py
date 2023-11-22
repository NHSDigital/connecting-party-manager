from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team import ProductTeam
from domain.core.fhir_transform import create_product_team_from_fhir_org_json
from domain.core.product import ProductTeam
from event.step_chain import StepChain


class ProductTeamRepository:
    def __init__(self, **kwargs):
        pass

    def write(self, *item):
        pass


def create_product_team(data, cache) -> ProductTeam:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    product_team, product_team_creation_event = create_product_team_from_fhir_org_json(
        fhir_org_json=event.json_body
    )
    return product_team


def save_product_team(data, cache) -> dict:
    product_team = data[create_product_team]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_NAME"],
        client=cache["DYNAMODB_CLIENT"],
    )
    return product_team_repo.write(product_team)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    create_product_team,
    save_product_team,
    set_http_status,
]
