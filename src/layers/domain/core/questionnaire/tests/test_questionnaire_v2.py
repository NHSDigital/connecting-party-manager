from datetime import datetime, timezone

from domain.core.questionnaire.v2 import Questionnaire


def test_questionnaire_response_created_on():
    questionnaire = Questionnaire(name="foo", version=1)
    questionnaire.add_question(name="bar", answer_types={str})
    response = questionnaire.respond(responses=[{"bar": ["BAR"]}])
    assert response.created_on.date() == datetime.now(timezone.utc).date()
