from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from hypothesis import given
from hypothesis.strategies import builds

from api.readProductTeam.tests.model import ReadProductTeamEvent

from ..steps import _read_product_team


@given(read_event=builds(ReadProductTeamEvent))
def test__read_product_team(read_event: ReadProductTeamEvent):
    event = APIGatewayProxyEvent(read_event.dict())
    product_team = _read_product_team(event=event)
    assert product_team == f"ProductTeam({read_event.pathParameters.id})"
