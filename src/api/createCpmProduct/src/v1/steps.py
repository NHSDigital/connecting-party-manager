from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.core.product_team.v3 import ProductTeam
from domain.repository.product_team_repository import ProductTeamRepository
from domain.response.validation_errors import mark_json_decode_errors_as_inbound
from event.aws.client import dynamodb_client
from event.step_chain import StepChain


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


def parse_incoming_cpm_product(data, cache) -> dict:
    json_body = data[parse_event_body]
    team_id = json_body.get("product_team_id", "")
    product_name = json_body.get("product_name", "")
    return team_id, product_name


def read_product_team(data, cache) -> ProductTeam:
    team_id, product_name = data[parse_incoming_cpm_product]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=dynamodb_client()
    )
    return product_team_repo.read(id=team_id)


def generate_cpm_product_id(data, cache) -> str:
    return "P.123-456"


def create_cpm_product(data, cache) -> CpmProduct:
    team_id, product_name = data[parse_incoming_cpm_product]
    product_team: ProductTeam = data[read_product_team]
    product_id = data[generate_cpm_product_id]
    product = product_team.create_cpm_product(product_id=product_id, name=product_name)
    return product


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    product: Product = data[create_cpm_product]
    return HTTPStatus.CREATED, str(product.id)


steps = [
    parse_event_body,
    parse_incoming_cpm_product,
    read_product_team,
    generate_cpm_product_id,
    create_cpm_product,
    # save_product_team,
    set_http_status,
]
