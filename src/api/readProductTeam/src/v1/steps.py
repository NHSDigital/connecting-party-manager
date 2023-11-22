from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team import ProductTeam
from domain.core.fhir_transform import create_fhir_model_from_product_team
from domain.core.product import OdsOrganisation, ProductTeam
from domain.core.user import User
from domain.fhir.r4.cpm_model import Organization
from event.step_chain import StepChain


class ProductTeamRepository:
    def __init__(self, **kwargs):
        pass

    def read(self, *item):
        return ProductTeam(
            id="123",
            organisation=OdsOrganisation(id="123", name="123"),
            owner=User(id="123", name="123"),
        )


def read_product_team(data, cache) -> ProductTeam:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    id = event.path_parameters["id"]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_NAME"],
        client=cache["DYNAMODB_CLIENT"],
    )
    return product_team_repo.read(id)


def product_team_to_fhir_org(data, cache) -> Organization:
    product_team = data[read_product_team]
    return create_fhir_model_from_product_team(product_team=product_team)


steps = [
    read_product_team,
    product_team_to_fhir_org,
]
