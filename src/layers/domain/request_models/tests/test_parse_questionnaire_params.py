import pytest
from domain.request_models import QuestionnairePathParams
from pydantic import ValidationError


@pytest.mark.parametrize(
    "id",
    ["abc123", "abc 123", " 123 ABC ", " 123_ABC "],
)
def test_read_questionnaire_path_params_pass(id: str):
    params = QuestionnairePathParams(questionnaire_id=id)
    assert params.dict() == {"questionnaire_id": id}


@pytest.mark.parametrize(
    "id",
    ["#abc123", "abc-123", "~123_ABC "],
)
def test_read_questionnaire_path_params_fail(id: str):
    with pytest.raises(ValidationError):
        QuestionnairePathParams(questionnaire_id=id)
