import pytest
from domain.core.questionnaire.v1 import NoSuchQuestionType
from domain.repository.questionnaire_repository.v1.deserialisers import (
    _deserialise_answer_type,
    _deserialise_rule,
)


def test__deserialise_rule():
    def _my_rule(value):
        return value

    class Rules:
        my_rule = _my_rule

    _rule = _deserialise_rule("my_rule", rules=Rules)
    assert _rule is _my_rule


@pytest.mark.parametrize(
    ["type_name", "_type"], [("str", str), ("int", int), ("bool", bool)]
)
def test__deserialise_answer_type(type_name: str, _type: type):
    assert (
        _deserialise_answer_type(
            answer_type_name=type_name,
            allowed_answer_types_lookup={"str": str, "int": int, "bool": bool},
        )
        is _type
    )


@pytest.mark.parametrize(
    "type_name",
    ["str", "int", "bool"],
)
def test__deserialise_question_types_not_found(type_name: str):
    with pytest.raises(NoSuchQuestionType):
        _deserialise_answer_type(
            answer_type_name=type_name, allowed_answer_types_lookup={}
        )
