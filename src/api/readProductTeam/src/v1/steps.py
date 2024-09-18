from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team import ProductTeam
from domain.fhir_translation.product_team import create_fhir_model_from_product_team
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from event.step_chain import StepChain


def read_product_team(data, cache) -> ProductTeam:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    id = event.path_parameters["id"]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=id)


def product_team_to_fhir_org(data, cache) -> dict:
    product_team = data[read_product_team]
    fhir_org = create_fhir_model_from_product_team(product_team=product_team)
    return fhir_org.dict()


steps = [
    read_product_team,
    product_team_to_fhir_org,
]
