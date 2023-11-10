import json
from uuid import UUID

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from api.createProductTeam.tests.data import organisation, product_team

from ..steps import _create_product_team, _parse_fhir_organisation


def test__create_product_team():
    org = _parse_fhir_organisation(organisation=organisation)
    assert org.dict(exclude_none=True) == organisation
    event = APIGatewayProxyEvent({"body": json.dumps(product_team)})
    created_product_team = _create_product_team(event=event)
    assert created_product_team.id == UUID(product_team["id"])
    assert created_product_team.name == product_team["name"]
    assert created_product_team.ods_code == product_team["ods_code"]
