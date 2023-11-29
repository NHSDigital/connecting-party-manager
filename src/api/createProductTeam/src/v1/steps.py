from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.fhir_transform import create_product_team_from_fhir_org_json
from domain.core.product_team import ProductTeam
from domain.ods import validate_ods_code
from event.step_chain import StepChain
from repository.product_team_repo import ProductTeamRepository


def create_product_team(data, cache) -> ProductTeam:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    product_team = create_product_team_from_fhir_org_json(fhir_org_json=event.json_body)
    return product_team


def validate_product_team_ods_code(data, cache) -> None:
    product_team: ProductTeam = data[create_product_team]
    validate_ods_code(ods_code=product_team.ods_code)


def save_product_team(data, cache) -> dict:
    product_team = data[create_product_team]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.write(entity=product_team)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    create_product_team,
    validate_product_team_ods_code,
    save_product_team,
    set_http_status,
]
