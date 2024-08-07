from datetime import date, datetime, time
from types import FunctionType
from typing import Type

import pytest
from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.questionnaire import (
    InvalidChoiceType,
    Question,
    Questionnaire,
    QuestionnaireResponse,
    TooManyAnswerTypes,
    custom_rules,
    validate_mandatory_questions_answered,
    validate_response_against_question,
)
from pydantic import ValidationError

QUESTIONNAIRE_NAME = "sample_questionnaire"
VERSION_1 = 1


@pytest.mark.parametrize(
    ["name", "version"],
    [[QUESTIONNAIRE_NAME, VERSION_1]],
)
def test_questionnaire_constructor(name: str, version: int):
    questionnaire = Questionnaire(name=name, version=version)

    assert questionnaire.name == name
    assert questionnaire.version == version
    assert questionnaire.questions is not None


@pytest.mark.parametrize(
    [
        "name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
    ],
    [
        [
            "Q1",
            "question 1",
            {str},
            False,
            False,
            set(),
            {"choice1", "choice2", "choice3"},
        ],
        ["Q2", "question 2", {int}, False, True, set(), {1, 2, 3}],
        ["Q3", "question 3", {bool}, False, False, set(), set()],
        ["Q4", "question 4", {datetime}, False, True, set(), set()],
    ],
)
def test_question_constructor(
    name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    question = Question(
        name=name,
        human_readable_name=human_readable_name,
        answer_types=answer_types,
        mandatory=mandatory,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert question.name == name
    assert question.human_readable_name == human_readable_name
    assert question.answer_types == answer_types
    assert question.mandatory == mandatory
    assert question.multiple == multiple
    assert question.validation_rules == validation_rules
    assert question.choices == choices


@pytest.mark.parametrize(
    [
        "name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
    ],
    [
        ["question1", "", {str}, True, False, None, {"choice1", "choice2", "choice3"}],
        ["question2", "", {int}, False, True, None, None],
    ],
)
def test_add_question(
    name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)

    result = questionnaire.add_question(
        name=name,
        human_readable_name=human_readable_name,
        answer_types=answer_types,
        mandatory=mandatory,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert result is not None
    assert name in questionnaire.questions


@pytest.mark.parametrize("question_name", ["question1", "question2", "question3"])
def test_cannot_add_duplicate_question(question_name: str):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name=question_name)

    with pytest.raises(DuplicateError) as error:
        questionnaire.add_question(name=question_name)

    assert str(error.value) == f"Question '{question_name}' already exists."


@pytest.mark.parametrize(
    [
        "name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
    ],
    [
        ["question1", "", {list}, False, False, None, None],
    ],
)
def test_cannot_add_question_of_wrong_type(
    name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    invalid_answer_types = {list}

    with pytest.raises(ValueError) as error:
        questionnaire.add_question(
            name=name,
            human_readable_name=human_readable_name,
            answer_types=answer_types,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )

    assert (
        error.value.errors()[0]["msg"]
        == f"Answer types {invalid_answer_types} are not allowed."
    )


@pytest.mark.parametrize(
    [
        "name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
    ],
    [
        ["question1", "", {dict, list}, False, False, None, None],
    ],
)
def test_cannot_add_question_of_wrong_type_2(
    name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set[str],
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    invalid_answer_types = {dict, list}

    with pytest.raises(ValueError) as error:
        questionnaire.add_question(
            name=name,
            human_readable_name=human_readable_name,
            answer_types=answer_types,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )

    assert (
        error.value.errors()[0]["msg"]
        == f"Answer types {invalid_answer_types} are not allowed."
    )


@pytest.mark.parametrize("name", ["question1", "question2", "question3"])
def test_has_question(name: str):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name=name)

    result = questionnaire.__contains__(name)

    assert result == True


@pytest.mark.parametrize(
    [
        "question_name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
    ],
    [
        ["question", "", {str}, False, False, {"not_custom_rule_function"}, None],
    ],
)
def test_invalid_question_validation_rules_type(
    question_name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set,
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)

    with pytest.raises(ValidationError) as error:
        questionnaire.add_question(
            name=question_name,
            human_readable_name=human_readable_name,
            answer_types=answer_types,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )

    assert error.value.errors()[0]["msg"] == "instance of function expected"


@pytest.mark.parametrize(
    [
        "name",
        "human_readable_name",
        "answer_types",
        "mandatory",
        "multiple",
        "validation_rules",
        "choices",
        "expected_error",
    ],
    [
        [
            "question1",
            "",
            {str, bool},
            False,
            False,
            None,
            {1, 2, 3},
            InvalidChoiceType,
        ],
        [
            "question2",
            "",
            {int},
            False,
            True,
            None,
            {"not_int", "not_int2"},
            InvalidChoiceType,
        ],
        [
            "question3",
            "",
            {str, bool},
            False,
            False,
            None,
            {"foo", "bar", True},
            TooManyAnswerTypes,
        ],
    ],
)
def test_invalid_question_choices_type(
    name: str,
    human_readable_name: str,
    answer_types: Type,
    mandatory: bool,
    multiple: bool,
    validation_rules: set[FunctionType],
    choices: set,
    expected_error: Exception,
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)

    # can't add question with set of choices that don't match question type
    with pytest.raises(expected_error):
        questionnaire.add_question(
            name=name,
            human_readable_name=human_readable_name,
            answer_types=answer_types,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )


@pytest.mark.parametrize(
    "response",
    [
        [
            {"question1": ["answer_a"]},
            {"not_a_question": [1]},
            {"question3": [True]},
        ],
        [
            {"not_a_question": ["answer_c"]},
            {"question2": [1]},
            {"question3": [False]},
        ],
    ],
)
def test_incorrect_questionnaire_answered_raises_error(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="question1")
    questionnaire.add_question(name="question2", answer_types={int})
    questionnaire.add_question(name="question3")

    with pytest.raises(ValidationError) as error:
        QuestionnaireResponse(questionnaire=questionnaire, responses=response)

    error_message = str(error.value)
    question_name = error_message.split("'")[1]
    assert (
        error.value.errors()[0]["msg"]
        == f"Unexpected answer for the question '{question_name}'. The questionnaire 'sample_questionnaire' does not contain this question."
    )


@pytest.mark.parametrize(
    "response",
    [
        [
            {"mandatory_question": ["answer"]},
            {"not_mandatory_question": [1]},
        ],
    ],
)
def test_mandatory_questions_answered(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="mandatory_question", mandatory=True)
    questionnaire.add_question(name="not_mandatory_question", answer_types={int})
    mandatory_questions = questionnaire.mandatory_questions
    answered_question_names = [
        question_name for (question_name, _), in map(dict.items, response)
    ]

    validate_mandatory_questions_answered(
        questionnaire_name=questionnaire.name,
        mandatory_questions=mandatory_questions,
        answered_question_names=answered_question_names,
    )
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {"mandatory_question": ["answer"]},
            {"not_mandatory_question": [1]},
        ],
    ],
)
def test_mandatory_questions_answered_successfully(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="mandatory_question", mandatory=True)
    questionnaire.add_question(name="not_mandatory_question", answer_types={int})
    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {"not_mandatory_question": [1]},
        ],
    ],
)
def test_mandatory_questions_not_answered(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="mandatory_question", mandatory=True)
    questionnaire.add_question(name="not_mandatory_question", answer_types={int})
    mandatory_questions = questionnaire.mandatory_questions
    answered_question_names = [
        question_name for (question_name, _), in map(dict.items, response)
    ]
    with pytest.raises(InvalidResponseError) as error:
        validate_mandatory_questions_answered(
            questionnaire_name=questionnaire.name,
            mandatory_questions=mandatory_questions,
            answered_question_names=answered_question_names,
        )
    assert (
        str(error.value)
        == f"Mandatory question 'mandatory_question' in questionnaire '{questionnaire.name}' has not been answered."
    )


@pytest.mark.parametrize(
    "response",
    [
        [
            {"not_mandatory_question": [1]},
        ],
    ],
)
def test_mandatory_questions_not_answered_raises_error(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="mandatory_question", mandatory=True)
    questionnaire.add_question(name="not_mandatory_question", answer_types={int})
    with pytest.raises(ValidationError) as error:
        QuestionnaireResponse(questionnaire=questionnaire, responses=response)

    assert (
        error.value.errors()[0]["msg"]
        == f"Mandatory question 'mandatory_question' in questionnaire '{questionnaire.name}' has not been answered."
    )


@pytest.mark.parametrize(
    "response",
    [
        [
            {"question1": ["answer_a", "answer_b"]},
            {"question2": [1, 2, 3]},
            {"question3": [True, False]},
        ],
        [
            {"question1": ["answer_c"]},
            {"question2": [4, 5]},
            {"question3": [False]},
        ],
    ],
)
def test_multiple_questions_responses_allowed(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="question1", multiple=True)
    questionnaire.add_question(name="question2", answer_types={int}, multiple=True)
    questionnaire.add_question(name="question3", answer_types={bool}, multiple=True)

    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        ["answer_a", "answer_b"],
        ["answer_c", "answer_d"],
    ],
)
def test_multiple_question_responses_allowed(response: list):
    question = Question(
        name="Question",
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {"question1": ["answer_a", "answer_b"]},
            {"question2": [1, 2, 3]},
            {"question3": [True, False]},
        ],
        [
            {"question1": ["answer_c", "answer_d"]},
            {"question2": [4, 5]},
            {"question3": [False]},
        ],
    ],
)
def test_multiple_questions_responses_not_allowed(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(name="question1")
    questionnaire.add_question(name="question2", answer_types={int})
    questionnaire.add_question(name="question3", answer_types={bool})

    with pytest.raises(ValidationError) as error:
        QuestionnaireResponse(questionnaire=questionnaire, responses=response)

    error_message = str(error.value)
    question_name = error_message.split("'")[1]
    response_given = error_message.split("Response given: ")[1].split(".")[0].strip()
    assert (
        error.value.errors()[0]["msg"]
        == f"Question '{question_name}' does not allow multiple responses. Response given: {response_given}."
    )


@pytest.mark.parametrize(
    "response",
    [
        ["answer_a", "answer_b"],
        ["answer_c", "answer_d"],
    ],
)
def test_multiple_question_responses_not_allowed(response: list):
    question = Question(
        name="Question",
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=False,
        validation_rules=set(),
        choices=set(),
    )

    with pytest.raises(InvalidResponseError) as error:
        validate_response_against_question(answers=response, question=question)

    assert (
        str(error.value)
        == f"Question 'Question' does not allow multiple responses. Response given: {response}."
    )


@pytest.mark.parametrize(
    "response",
    [
        [
            {"String or integer response": ["answer_a", 1]},
            {"Integer or boolean": [1]},
            {"Integer or boolean or string multiple": [True, 1, "string"]},
        ],
    ],
)
def test_multiple_answer_types_allowed(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name="String or integer response", answer_types={str, int}, multiple=True
    )
    questionnaire.add_question(name="Integer or boolean", answer_types={int, bool})
    questionnaire.add_question(
        name="Integer or boolean or string multiple",
        answer_types={str, int, bool},
        multiple=True,
    )

    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.fixture
def standard_questionnaire() -> Questionnaire:
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name="String response", answer_types={str}, multiple=True
    )
    questionnaire.add_question(name="Integer response", answer_types={int})
    questionnaire.add_question(name="Boolean response", answer_types={bool})
    questionnaire.add_question(name="Date-Time response", answer_types={datetime})
    questionnaire.add_question(name="Decimal response", answer_types={float})
    questionnaire.add_question(name="Date response", answer_types={date})
    questionnaire.add_question(name="Time response", answer_types={time})
    return questionnaire


@pytest.mark.parametrize(
    "response",
    [
        [
            {"String response": ["answer_a", "answer_b"]},
            {"Integer response": [1]},
            {"Boolean response": [True]},
            {"Date-Time response": [datetime(2024, 1, 24, 14, 21, 7, 484991)]},
            {"Decimal response": [1.1]},
            {"Date response": [datetime(2024, 1, 24)]},
            {"Time response": [datetime.strptime("14:21:07", "%H:%M:%S").time()]},
        ],
    ],
)
def test_valid_questionnaire_responses_types(
    response: list[dict[str, list]], standard_questionnaire: Questionnaire
):
    QuestionnaireResponse(questionnaire=standard_questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {"String response": [1]},
        ],
        [
            {"Integer response": ["answer"]},
        ],
        [
            {"Boolean response": [1.1]},
        ],
        [
            {"Date-Time response": [1]},
        ],
        [
            {"Decimal response": [False]},
        ],
        [
            {"Date response": ["answer"]},
        ],
        [
            {"Time response": [True]},
        ],
    ],
)
def test_invalid_questionnaire_responses_types_raises_error(
    response: list[dict[str, list]], standard_questionnaire: Questionnaire
):
    with pytest.raises(ValidationError) as error:
        QuestionnaireResponse(questionnaire=standard_questionnaire, responses=response)

    error_message = str(error.value)
    question_name = error_message.split("'")[1]
    response_given_str = error_message.split("Response '")[1].split("'")[0]
    try:
        response_given = eval(response_given_str)  # Can't evaluate strings or datetime
    except NameError:
        response_given = response_given_str
    response_type = repr(type(response_given))
    expected_type = standard_questionnaire.questions[question_name].answer_types

    assert (
        error.value.errors()[0]["msg"]
        == f"Question '{question_name}' rule 'validate_answer_types' failed validation for response '{response_given}' with error: Question '{question_name}' expects type {expected_type}. Response '{response_given}' is of type '{response_type}'."
    )


@pytest.mark.parametrize(
    "response",
    [
        ["answer"],
    ],
)
def test_valid_question_response_type_string(response: list):
    question = Question(
        name="String response",
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    ["answer_type", "response"],
    [
        [str, 1],
        [int, "a"],
        [bool, 1],
        [datetime, "a"],
        [float, "1.2"],
        [date, "a"],
    ],
)
def test_invalid_question_response(answer_type: type, response: any):
    question = Question(
        name="question",
        human_readable_name="",
        answer_types={answer_type},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    with pytest.raises(InvalidResponseError) as error:
        validate_response_against_question(answers=[response], question=question)

    assert (
        str(error.value)
        == f"Question '{question.name}' rule 'validate_answer_types' failed validation for response '{response}' with error: Question '{question.name}' expects type {question.answer_types}. Response '{response}' is of type '{type(response)}'."
    )


@pytest.mark.parametrize(
    "response",
    [
        [1],
    ],
)
def test_valid_question_response_type_integer(response: list):
    question = Question(
        name="Integer response",
        human_readable_name="",
        answer_types={int},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [True],
    ],
)
def test_valid_question_response_type_bool(response: list):
    question = Question(
        name="Boolean response",
        human_readable_name="",
        answer_types={bool},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [datetime(2024, 1, 24, 14, 21, 7, 484991)],
    ],
)
def test_valid_question_response_type_datetime(response: list):
    question = Question(
        name="Date-Time response",
        human_readable_name="",
        answer_types={datetime},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [1.27],
    ],
)
def test_valid_question_response_type_float(response: list):
    question = Question(
        name="Decimal response",
        human_readable_name="",
        answer_types={float},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [datetime(2024, 1, 24)],
    ],
)
def test_valid_question_response_type_date(response: list):
    question = Question(
        name="Date response",
        human_readable_name="",
        answer_types={date},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [datetime.strptime("14:21:07", "%H:%M:%S").time()],
    ],
)
def test_valid_question_response_type_time(response: list):
    question = Question(
        name="Time response",
        human_readable_name="",
        answer_types={time},
        mandatory=False,
        multiple=True,
        validation_rules=set(),
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {"question1": ["answer_a", "answer_b"]},
            {"question2": [1, 2, 3]},
        ],
        [
            {"question1": ["answer_c"]},
            {"question2": [4, 5]},
        ],
    ],
)
def test_valid_questionnaire_responses_choices(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name="question1", multiple=True, choices={"answer_a", "answer_b", "answer_c"}
    )
    questionnaire.add_question(
        name="question2",
        answer_types={int},
        multiple=True,
        choices={1, 2, 3, 4, 5, 6, 7},
    )

    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
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
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=False,
        validation_rules=set(),
        choices={"answer_a", "answer_b", "answer_c"},
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


# Validation rule questions:
EMPTY_STR_QUESTION_NAME = "empty string"
EMPTY_STR_OR_INT_QUESTION_NAME = "empty string or integer"
URL_QUESTION_NAME = "url"


@pytest.mark.parametrize(
    "response",
    [
        [
            {URL_QUESTION_NAME: ["https://www.example.com"]},
        ],
    ],
)
def test_valid_questionnaire_responses_rule_url(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name=URL_QUESTION_NAME,
        validation_rules={custom_rules.url},
    )

    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [["https://www.example.com"]],
)
def test_valid_question_response_rule_url(response: list):
    question = Question(
        name=URL_QUESTION_NAME,
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=False,
        validation_rules={custom_rules.url},
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [
        [
            {EMPTY_STR_QUESTION_NAME: [""]},
            {EMPTY_STR_OR_INT_QUESTION_NAME: ["", 1]},
        ],
    ],
)
def test_valid_questionnaire_responses_rule_empty_str(response: list[dict[str, list]]):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name=EMPTY_STR_QUESTION_NAME,
        validation_rules={custom_rules.empty_str},
    )
    questionnaire.add_question(
        name=EMPTY_STR_OR_INT_QUESTION_NAME,
        answer_types={str, int},
        multiple=True,
        validation_rules={custom_rules.empty_str},
    )

    QuestionnaireResponse(questionnaire=questionnaire, responses=response)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [[""]],
)
def test_valid_question_response_rule_empty_str(response: list[dict[str, list]]):
    question = Question(
        name=EMPTY_STR_QUESTION_NAME,
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=False,
        validation_rules={custom_rules.empty_str},
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "response",
    [["", 1]],
)
def test_valid_question_response_rule_empty_str_2(response: list[dict[str, list]]):
    question = Question(
        name=EMPTY_STR_QUESTION_NAME,
        human_readable_name="",
        answer_types={str, int},
        mandatory=False,
        multiple=True,
        validation_rules={custom_rules.empty_str},
        choices=set(),
    )

    validate_response_against_question(answers=response, question=question)
    # if no error raised, the test has implicitly passed


@pytest.mark.parametrize(
    "responses",
    [
        [
            {URL_QUESTION_NAME: ["not_a_url"]},
            {EMPTY_STR_QUESTION_NAME: ["not an empty string"]},
        ],
    ],
)
def test_invalid_questionnaire_response_rules_raises_error(
    responses: list[dict[str, list]]
):
    questionnaire = Questionnaire(name=QUESTIONNAIRE_NAME, version=VERSION_1)
    questionnaire.add_question(
        name=URL_QUESTION_NAME,
        validation_rules={custom_rules.url},
    )
    questionnaire.add_question(
        name=EMPTY_STR_QUESTION_NAME,
        validation_rules={custom_rules.empty_str},
    )

    with pytest.raises(ValidationError) as error:
        QuestionnaireResponse(questionnaire=questionnaire, responses=responses)

    assert (
        error.value.errors()[0]["msg"]
        == f"Question '{URL_QUESTION_NAME}' rule 'url' failed validation for response 'not_a_url' with error: Invalid URL format."
    )
    assert (
        error.value.errors()[1]["msg"]
        == f"Question '{EMPTY_STR_QUESTION_NAME}' rule 'empty_str' failed validation for response 'not an empty string' with error: Expected empty string."
    )


@pytest.mark.parametrize(
    "response",
    [["not_a_url"]],
)
def test_invalid_question_response_rule_url_raises_error(response: list):
    question = Question(
        name=URL_QUESTION_NAME,
        human_readable_name="",
        answer_types={str},
        mandatory=False,
        multiple=False,
        validation_rules={custom_rules.url},
        choices=set(),
    )

    with pytest.raises(InvalidResponseError) as error:
        validate_response_against_question(answers=response, question=question)

    assert (
        str(error.value)
        == f"Question '{question.name}' rule 'url' failed validation for response '{response[0]}' with error: Invalid URL format."
    )


@pytest.mark.parametrize(
    "response",
    [[1, "not_a_empty_string"]],
)
def test_invalid_question_response_rule_empty_str_raises_error(response: list):
    question = Question(
        name=EMPTY_STR_QUESTION_NAME,
        human_readable_name="",
        answer_types={str, int},
        mandatory=False,
        multiple=True,
        validation_rules={custom_rules.empty_str},
        choices=set(),
    )

    with pytest.raises(InvalidResponseError) as error:
        validate_response_against_question(answers=response, question=question)

    assert (
        str(error.value)
        == f"Question '{question.name}' rule 'empty_str' failed validation for response '{response[1]}' with error: Expected empty string."
    )
