from datetime import date, datetime, time
from types import FunctionType
from typing import Type, TypeVar

import pytest
from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.questionnaire import (
    Question,
    Questionnaire,
    QuestionnaireResponse,
    validate_response_against_question,
)
from domain.core.questionnaire_validation_custom_rules import url
from pydantic import ValidationError

T = TypeVar("T")


@pytest.mark.parametrize(
    ["name", "version"],
    [["sample_questionnaire", 1]],
)
def test_questionnaire_constructor(name: str, version: int):
    questionnaire = Questionnaire(name=name, version=version)

    assert questionnaire.name == name
    assert questionnaire.version == version
    assert questionnaire.questions is not None


@pytest.mark.parametrize(
    ["name", "answer_type", "multiple", "validation_rules", "choices"],
    [
        ["question1", str, False, None, {"choice1", "choice2", "choice3"}],
        ["question2", int, True, None, {1, 2, 3}],
        ["question3", bool, False, None, None],
        ["question4", datetime, True, None, None],
    ],
)
def test_question_constructor(
    name: str,
    answer_type: Type,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    question = Question(
        name=name,
        answer_type=answer_type,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert question.name == name
    assert question.answer_type == answer_type
    assert question.multiple == multiple
    assert question.validation_rules == validation_rules
    assert question.choices == choices


@pytest.mark.parametrize(
    ["name", "answer_type", "multiple", "validation_rules", "choices"],
    [
        ["question1", str, False, None, {"choice1", "choice2", "choice3"}],
        ["question2", int, True, None, None],
    ],
)
def test_add_question(
    name: str,
    answer_type: Type,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    questionnaire = Questionnaire(name="sample_questionnaire", version=1)

    result = questionnaire.add_question(
        name=name,
        answer_type=answer_type,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert result is not None
    assert name in questionnaire.questions


@pytest.mark.parametrize("question_name", ["question1", "question2", "question3"])
def test_cannot_add_duplicate_question(question_name: str):
    questionnaire = Questionnaire(name="questionnaire", version=1)
    questionnaire.add_question(name=question_name)

    with pytest.raises(DuplicateError) as error:
        questionnaire.add_question(name=question_name)

    assert str(error.value) == f"Question '{question_name}' already exists."


@pytest.mark.parametrize(
    ["name", "answer_type", "multiple", "validation_rules", "choices"],
    [
        ["question1", list, False, None, {"choice1", "choice2", "choice3"}],
    ],
)
def test_cannot_add_question_of_wrong_type(
    name: str,
    answer_type: Type,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    questionnaire = Questionnaire(name="sample_questionnaire", version=1)

    with pytest.raises(ValueError) as error:
        result = questionnaire.add_question(
            name=name,
            answer_type=answer_type,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )


@pytest.mark.parametrize("name", ["question1", "question2", "question3"])
def test_has_question(name: str):
    questionnaire = Questionnaire(name="questionnaire", version=1)
    questionnaire.add_question(name=name)

    result = questionnaire.__contains__(name)

    assert result == True


@pytest.mark.parametrize(
    ["question_name", "answer_type", "multiple", "validation_rules", "choices"],
    [
        ["question", str, False, {"not_custom_rule_function"}, None],
    ],
)
def test_invalid_question_validation_rules_type(
    question_name: str,
    answer_type: Type,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[T],
):
    questionnaire = Questionnaire(name="questionnaire", version=1)

    with pytest.raises(ValidationError) as error:
        questionnaire.add_question(
            name=question_name,
            answer_type=answer_type,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )

    assert error.value.errors()[0]["msg"] == "instance of function expected"


@pytest.mark.parametrize(
    ["name", "answer_type", "multiple", "validation_rules", "choices"],
    [
        ["question1", str, False, None, {1, 2, 3}],
        ["question2", int, True, None, {"not_int", "not_int2"}],
    ],
)
def test_invalid_question_choices_type(
    name: str,
    answer_type: Type,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[T],
):
    questionnaire = Questionnaire(name="questionnaire", version=1)

    # can't add question with set of choices that don't match question type
    with pytest.raises(ValueError) as error:
        questionnaire.add_question(
            name=name,
            answer_type=answer_type,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )


@pytest.mark.parametrize(
    "response",
    [
        [
            ("question1", ["answer_a", "answer_b"]),
            ("not_a_question", [1]),
            ("question3", [True]),
        ],
        [
            ("not_a_question", ["answer_c"]),
            ("question2", [1]),
            ("question3", [False]),
        ],
    ],
)
def test_incorrect_questionnaire_answered(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="question1")
    questionnaire.add_question(name="question2", answer_type=int)
    questionnaire.add_question(name="question3")

    with pytest.raises(ValidationError) as error:
        questionnaire_response = QuestionnaireResponse(
            questionnaire=questionnaire, responses=response
        )


@pytest.mark.parametrize(
    "response",
    [
        [
            ("question1", ["answer_a", "answer_b"]),
            ("question2", [1, 2, 3]),
            ("question3", [True, False]),
        ],
        [
            ("question1", ["answer_c"]),
            ("question2", [4, 5]),
            ("question3", [False]),
        ],
    ],
)
def test_multiple_questions_responses_allowed(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="question1", multiple=True)
    questionnaire.add_question(name="question2", answer_type=int, multiple=True)
    questionnaire.add_question(name="question3", answer_type=bool, multiple=True)

    questionnaire_response = QuestionnaireResponse(
        questionnaire=questionnaire, responses=response
    )

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        ["answer_a", "answer_b"],
        ["answer_c", "answer_d"],
    ],
)
def test_multiple_question_responses_allowed(response: list):
    question = Question(name="Question", answer_type=str, multiple=True)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            ("question1", ["answer_a", "answer_b"]),
            ("question2", [1, 2, 3]),
            ("question3", [True, False]),
        ],
        [
            ("question1", ["answer_c", "answer_d"]),
            ("question2", [4, 5]),
            ("question3", [False]),
        ],
    ],
)
def test_multiple_questions_responses_not_allowed(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="question1")
    questionnaire.add_question(name="question2", answer_type=int)
    questionnaire.add_question(name="question3", answer_type=bool)

    with pytest.raises(ValidationError) as error:
        questionnaire_response = QuestionnaireResponse(
            questionnaire=questionnaire, responses=response
        )


@pytest.mark.parametrize(
    "response",
    [
        ["answer_a", "answer_b"],
        ["answer_c", "answer_d"],
    ],
)
def test_multiple_question_responses_not_allowed(response: list):
    question = Question(name="Question", answer_type=str, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [
            ("String response", ["answer_a", "answer_b"]),
            ("Integer response", [1]),
            ("Boolean response", [True]),
            ("Date-Time response", [datetime(2024, 1, 24, 14, 21, 7, 484991)]),
            ("Decimal response", [1.1]),
            ("Date response", [datetime(2024, 1, 24)]),
            ("Time response", [datetime.strptime("14:21:07", "%H:%M:%S").time()]),
        ],
    ],
)
def test_valid_questionnaire_responses_types(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="String response", answer_type=str, multiple=True)
    questionnaire.add_question(name="Integer response", answer_type=int)
    questionnaire.add_question(name="Boolean response", answer_type=bool)
    questionnaire.add_question(name="Date-Time response", answer_type=datetime)
    questionnaire.add_question(name="Decimal response", answer_type=float)
    questionnaire.add_question(name="Date response", answer_type=date)
    questionnaire.add_question(name="Time response", answer_type=time)

    questionnaire_response = QuestionnaireResponse(
        questionnaire=questionnaire, responses=response
    )

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            ("String response", ["answer_a", "answer_b"]),
            ("Integer response", ["answer"]),
            ("Boolean response", [1]),
            ("Date-Time response", [1]),
            ("Decimal response", [1.1]),
            ("Date response", [datetime(2024, 1, 24)]),
            ("Time response", [False]),
        ],
        [
            ("String response", ["answer", 1]),
            ("Integer response", [1.27]),
            ("Boolean response", [True]),
            ("Date-Time response", [datetime(2024, 1, 24, 14, 21, 7, 484991)]),
            ("Decimal response", [1.1]),
            ("Date response", [True]),
            ("Time response", [datetime.strptime("14:21:07", "%H:%M:%S").time()]),
        ],
        [
            ("String response", ["answer_a", "answer_b"]),
            ("Integer response", [1]),
            ("Boolean response", [datetime(2024, 1, 24, 14, 21, 7, 484991)]),
            ("Date-Time response", [1]),
            ("Decimal response", [False]),
            ("Date response", [datetime(2024, 1, 24)]),
            ("Time response", ["answer"]),
        ],
    ],
)
def test_invalid_questionnaire_responses_types(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="String response", answer_type=str, multiple=True)
    questionnaire.add_question(name="Integer response", answer_type=int)
    questionnaire.add_question(name="Boolean response", answer_type=bool)
    questionnaire.add_question(name="Date-Time response", answer_type=datetime)
    questionnaire.add_question(name="Decimal response", answer_type=float)
    questionnaire.add_question(name="Date response", answer_type=date)
    questionnaire.add_question(name="Time response", answer_type=time)

    with pytest.raises(ValidationError) as error:
        questionnaire_response = QuestionnaireResponse(
            questionnaire=questionnaire, responses=response
        )


@pytest.mark.parametrize(
    "response",
    [
        ["answer"],
    ],
)
def test_valid_question_response_type_string(response: list):
    question = Question(name="String response", answer_type=str, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [1],
    ],
)
def test_invalid_question_response_type_string(response: list):
    question = Question(name="String response", answer_type=str, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [1],
    ],
)
def test_valid_question_response_type_integer(response: list):
    question = Question(name="Integer response", answer_type=int, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        ["answer"],
    ],
)
def test_invalid_question_response_type_integer(response: list):
    question = Question(name="Integer response", answer_type=int, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [True],
    ],
)
def test_valid_question_response_type_bool(response: list):
    question = Question(name="Boolean response", answer_type=bool, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [1],
    ],
)
def test_invalid_question_response_type_bool(response: list):
    question = Question(name="Boolean response", answer_type=bool, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [datetime(2024, 1, 24, 14, 21, 7, 484991)],
    ],
)
def test_valid_question_response_type_datetime(response: list):
    question = Question(name="Date-Time response", answer_type=datetime, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        ["answer"],
    ],
)
def test_invalid_question_response_type_datetime(response: list):
    question = Question(name="Date-Time response", answer_type=datetime, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [1.27],
    ],
)
def test_valid_question_response_type_float(response: list):
    question = Question(name="Decimal response", answer_type=float, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [True],
    ],
)
def test_invalid_question_response_type_float(response: list):
    question = Question(name="Decimal response", answer_type=float, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [datetime(2024, 1, 24)],
    ],
)
def test_valid_question_response_type_date(response: list):
    question = Question(name="Date response", answer_type=date, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [False],
    ],
)
def test_invalid_question_response_type_date(response: list):
    question = Question(name="Date response", answer_type=date, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [datetime.strptime("14:21:07", "%H:%M:%S").time()],
    ],
)
def test_valid_question_response_type_time(response: list):
    question = Question(name="Time response", answer_type=time, multiple=False)

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [1],
    ],
)
def test_invalid_question_response_type_time(response: list):
    question = Question(name="Time response", answer_type=time, multiple=False)

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [
            ("question1", ["answer_a", "answer_b"]),
            ("question2", [1, 2, 3]),
        ],
        [
            ("question1", ["answer_c"]),
            ("question2", [4, 5]),
        ],
    ],
)
def test_valid_questionnaire_responses_choices(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="question1", multiple=True, choices={"answer_a", "answer_b", "answer_c"}
    )
    questionnaire.add_question(
        name="question2", answer_type=int, multiple=True, choices={1, 2, 3, 4, 5, 6, 7}
    )

    questionnaire_response = QuestionnaireResponse(
        questionnaire=questionnaire, responses=response
    )

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        ["answer_a"],
        ["answer_b"],
        ["answer_c"],
    ],
)
def test_valid_question_response_choice(response: list):
    question = Question(
        name="Question",
        answer_type=str,
        multiple=False,
        choices={"answer_a", "answer_b", "answer_c"},
    )

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            ("question1", ["not_in_choices"]),
            ("question2", [27, 7, 2]),
        ],
        [
            ("question1", ["not_in_choices"]),
            ("question2", [2, 3, 4]),
        ],
    ],
)
def test_invalid_questionnaire_responses_choices(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="question1", multiple=True, choices={"a1", "a2", "answer3", "a4"}
    )
    questionnaire.add_question(
        name="question2",
        answer_type=int,
        multiple=True,
        choices={3, 7, 27, 38, 59, 100},
    )

    with pytest.raises(ValidationError) as error:
        questionnaire_response = QuestionnaireResponse(
            questionnaire=questionnaire, responses=response
        )


@pytest.mark.parametrize(
    "response",
    [
        ["not_in_choices"],
    ],
)
def test_invalid_question_response_choice(response: list):
    question = Question(
        name="Question", answer_type=str, multiple=False, choices=["a", "b", "c"]
    )

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)


@pytest.mark.parametrize(
    "response",
    [
        [
            ("url", ["https://www.example.com"]),
        ],
    ],
)
def test_valid_questionnaire_responses_rules(response: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="url", validation_rules={url})

    questionnaire_response = QuestionnaireResponse(
        questionnaire=questionnaire, responses=response
    )

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [["https://www.example.com"]],
)
def test_valid_question_response_rule(response: list):
    question = Question(
        name="url", answer_type=str, multiple=False, validation_rules={url}
    )

    result = validate_response_against_question(answers=response, question=question)

    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "responses",
    [
        ("url", ["not_a_url"]),
    ],
)
def test_invalid_questionnaire_response_rules(responses: list[tuple[str, list]]):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="url", validation_rules={url})

    with pytest.raises(ValidationError) as error:
        questionnaire_response = QuestionnaireResponse(
            questionnaire=questionnaire, responses=responses
        )


@pytest.mark.parametrize(
    "response",
    [["not_a_url"]],
)
def test_invalid_question_response_rule(response: list):
    question = Question(
        name="url", answer_type=str, multiple=False, validation_rules={url}
    )

    with pytest.raises(InvalidResponseError) as error:
        result = validate_response_against_question(answers=response, question=question)
