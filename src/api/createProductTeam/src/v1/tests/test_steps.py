import json

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from api.createProductTeam.tests.data import product_team

from ..steps import _create_product_team


def test__create_product_team():
    event = APIGatewayProxyEvent({"body": json.dumps(product_team)})
    created_product_team, created_product_team_event = _create_product_team(event=event)
    assert created_product_team.id == product_team["id"]
    assert created_product_team.name == product_team["name"]

    assert created_product_team.organisation.id == product_team["organisation"]["id"]
    assert (
        created_product_team.organisation.name == product_team["organisation"]["name"]
    )

    assert created_product_team.owner.id == product_team["owner"]["id"]
    assert created_product_team.owner.name == product_team["owner"]["name"]
