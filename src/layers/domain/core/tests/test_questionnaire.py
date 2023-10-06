import pytest
from domain.core.error import DuplicateError
from domain.core.questionnaire import Question, Questionnaire, QuestionType


@pytest.mark.parametrize(
    ["id", "name"],
    [
        ["x", "X"],
        ["y", "Y"],
        ["z", "Z"],
    ],
)
def test_questionnaire_constructor(id: str, name: str):
    subject = Questionnaire(id, name)

    assert subject.id == id, "id"
    assert subject.name == name, "name"
    assert subject._questions is not None, "questions"


@pytest.mark.parametrize(
    ["name", "type", "multiple"],
    [
        ["a", QuestionType.STRING, False],
        ["b", QuestionType.INT, True],
        ["c", QuestionType.BOOL, False],
        ["d", QuestionType.DATE_TIME, True],
    ],
)
def test_question_constructor(name: str, type: QuestionType, multiple: bool):
    subject = Question(name, type, multiple)

    assert subject.name == name, "name"
    assert subject.type == type, "type"
    assert subject.multiple == multiple, "multiple"


@pytest.mark.parametrize(
    ["name", "type", "multiple"],
    [
        ["alpha", QuestionType.STRING, False],
        ["beta", QuestionType.INT, True],
    ],
)
def test_add_question(name: str, type: QuestionType, multiple: bool):
    subject = Questionnaire("id", "name")

    result = subject.add_question(name, type=type, multiple=multiple)

    assert result is not None, "result"
    assert name in [q.name for q in subject._questions], "name in questions"


@pytest.mark.parametrize("name", ["alpha", "beta", "gamma"])
def test_cannot_add_duplicate_question(name: str):
    subject = Questionnaire("id", "name")
    subject.add_question(name)

    with pytest.raises(DuplicateError):
        subject.add_question(name)


@pytest.mark.parametrize("name", ["alpha", "beta", "gamma"])
def test_has_question(name: str):
    subject = Questionnaire("id", "name")
    subject.add_question(name)

    assert name in subject, "has_question"


@pytest.mark.parametrize(
    ["name", "missing"],
    [["alpha", "not_present"], ["beta", "look_elsewhere"], ["gamma", "nope"]],
)
def test_doesnt_have_question(name: str, missing: str):
    subject = Questionnaire("id", "name")
    subject.add_question(name)

    assert name not in subject, "not has_question()"
