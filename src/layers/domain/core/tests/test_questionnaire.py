from datetime import datetime

import pytest
from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.questionnaire import (
    Question,
    Questionnaire,
    QuestionnaireResponseValidator,
    QuestionType,
)


@pytest.mark.parametrize(
    ["name", "version"],
    [["sample_questionnaire", 1]],
)
def test_questionnaire_constructor(name: str, version: int):
    subject = Questionnaire(name=name, version=version)

    assert subject.name == name, "name"
    assert subject.version == version, "version"
    assert subject.questions is not None, "questions"


@pytest.mark.parametrize(
    ["name", "type", "multiple", "validation_rules", "choices"],
    [
        ["a", QuestionType.STRING, False, [], ["x", "y", "z"]],
        ["b", QuestionType.INT, True, ["url"], []],
        ["c", QuestionType.BOOL, False, [], []],
        ["d", QuestionType.DATE_TIME, True, [], []],
    ],
)
def test_question_constructor(
    name: str,
    type: QuestionType,
    multiple: bool,
    validation_rules: list[str],
    choices: list[str],
):
    subject = Question(
        name=name,
        type=type,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert subject.name == name, "name"
    assert subject.type == type, "type"
    assert subject.multiple == multiple, "multiple"
    assert subject.validation_rules == validation_rules, "validation_rules"
    assert subject.choices == choices, "choices"


@pytest.mark.parametrize(
    ["name", "type", "multiple", "validation_rules", "choices"],
    [
        ["alpha", QuestionType.STRING, False, [], ["x", "y", "z"]],
        ["beta", QuestionType.INT, True, ["url"], []],
    ],
)
def test_add_question(
    name: str,
    type: QuestionType,
    multiple: bool,
    validation_rules: list[str],
    choices: list[str],
):
    subject = Questionnaire(name="sample_questionnaire", version=1)

    result = subject.add_question(
        name=name,
        type=type,
        multiple=multiple,
        validation_rules=validation_rules,
        choices=choices,
    )

    assert result is not None, "result"
    assert name in [q.name for q in subject.questions], "name in questions"


@pytest.mark.parametrize("name", ["alpha", "beta", "gamma"])
def test_cannot_add_duplicate_question(name: str):
    subject = Questionnaire(name="questionnaire", version=1)
    subject.add_question(name=name)

    with pytest.raises(DuplicateError):
        subject.add_question(name=name)


@pytest.mark.parametrize("name", ["alpha", "beta", "gamma"])
def test_has_question(name: str):
    subject = Questionnaire(name="questionnaire", version=1)
    subject.add_question(name=name)

    result = subject.__contains__(name)

    assert result == True, "has_question"


@pytest.mark.parametrize(
    ["name", "missing"],
    [["alpha", "not_present"], ["beta", "look_elsewhere"], ["gamma", "nope"]],
)
def test_doesnt_have_question(name: str, missing: str):
    subject = Questionnaire(name="questionnaire", version=1)

    assert name not in subject, "not has_question"


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 2,
            "What is your favorite color?": "pink",
            "interactionID": "xxx",
        }
    ],
)
def test_correct_questionnaire_answered(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(name="What is your favorite color?")
    questionnaire.add_question(name="interactionID")

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_responses_correspond_to_questionnaire()

    assert result == True, "correct questionnaire answered"


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 2,
            "What is your favorite color?": "pink",
            "interactionID": "xxx",
        },
        {
            "How many years of experience do you have in programming?": 2,
            "What is your favorite animal?": "dog",
            "interactionID": "xxx",
        },
        {
            "How many years of experience do you have in programming?": 2,
            "What is your favorite color?": "pink",
            "What is your favourite food?": "Chicken nuggets",
        },
    ],
)
def test_incorrect_questionnaire_answered(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(name="What is your favorite animal?")
    questionnaire.add_question(name="What is your favourite food?")

    with pytest.raises(InvalidResponseError):
        result = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_responses_correspond_to_questionnaire()


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 1,
            "What is your favorite animal?": ["dog", "cat"],
            "What is your favourite food?": "pasta",
        }
    ],
)
def test_multiple_responses_allowed(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(
        name="What is your favorite animal?",
        choices=["dog", "cat", "pig"],
        multiple=True,
    )
    questionnaire.add_question(
        name="What is your favourite food?",
        choices=["chicken", "pasta", "rice"],
        multiple=True,
    )

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_multiple_responses_allowed()

    assert result == True


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": [1, 10],
            "What is your favorite animal?": ["whale"],
            "What is your favourite food?": ["chocolate", "cake"],
        }
    ],
)
def test_multiple_responses_not_allowed(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
        multiple=True,
    )
    questionnaire.add_question(
        name="What is your favorite animal?", choices=["dog", "cat", "pig"]
    )
    questionnaire.add_question(
        name="What is your favourite food?", choices=["chicken", "pasta", "rice"]
    )

    with pytest.raises(InvalidResponseError):
        result2 = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_multiple_responses_allowed()


@pytest.mark.parametrize(
    "response",
    [
        {
            "String response": "pink",
            "Integer response": 2,
            "Boolean response": True,
            "Date-Time response": datetime(2024, 1, 24, 14, 21, 7, 484991),
            "Decimal response": 1.27,
            "Date response": datetime(2024, 1, 24),
            "Time response": datetime.strptime("14:21:07", "%H:%M:%S").time(),
        }
    ],
)
def test_valid_questionnaire_response_types(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="String response", type=QuestionType.STRING)
    questionnaire.add_question(name="Integer response", type=QuestionType.INT)
    questionnaire.add_question(name="Boolean response", type=QuestionType.BOOL)
    questionnaire.add_question(name="Date-Time response", type=QuestionType.DATE_TIME)
    questionnaire.add_question(name="Decimal response", type=QuestionType.DECIMAL)
    questionnaire.add_question(name="Date response", type=QuestionType.DATE)
    questionnaire.add_question(name="Time response", type=QuestionType.TIME)

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_types()
    result2 = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_and_get_invalid_responses()

    assert result == []
    assert result2[1] == "invalid response rules: []"


@pytest.mark.parametrize(
    "response",
    [
        {
            "String response": 1,
            "Integer response": "alpha",
            "Boolean response": "True",
            "Date-Time response": "2024-01-01 12:30:00",
            "Decimal response": "15.0",
            "Date response": "2024-01-01",
            "Time response": "12:30:00",
        }
    ],
)
def test_invalid_questionnaire_response_types(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(name="String response", type=QuestionType.STRING)
    questionnaire.add_question(name="Integer response", type=QuestionType.INT)
    questionnaire.add_question(name="Boolean response", type=QuestionType.BOOL)
    questionnaire.add_question(name="Date-Time response", type=QuestionType.DATE_TIME)
    questionnaire.add_question(name="Decimal response", type=QuestionType.DECIMAL)
    questionnaire.add_question(name="Date response", type=QuestionType.DATE)
    questionnaire.add_question(name="Time response", type=QuestionType.TIME)

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_types()

    assert len(result) == 7

    with pytest.raises(InvalidResponseError):
        result2 = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_and_get_invalid_responses()


# def test_valid_questionnaire_response_rules():
# not got any rules yet?

# def test_invalid_questionnaire_response_rules():


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 1,
            "What is your favorite animal?": "dog",
            "What is your favourite food?": "pasta",
        }
    ],
)
def test_valid_questionnaire_response_choices(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(
        name="What is your favorite animal?", choices=["dog", "cat", "pig"]
    )
    questionnaire.add_question(
        name="What is your favourite food?", choices=["chicken", "pasta", "rice"]
    )

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_choices()
    result2 = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_and_get_invalid_responses()

    assert result == []
    assert result2[2] == "invalid response choices: []"


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 1,
            "What is your favorite animal?": "whale",
            "What is your favourite food?": "chocolate",
        }
    ],
)
def test_invalid_questionnaire_response_choices(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(
        name="What is your favorite animal?", choices=["dog", "cat", "pig"]
    )
    questionnaire.add_question(
        name="What is your favourite food?", choices=["chicken", "pasta", "rice"]
    )

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_choices()

    assert len(result) == 2

    with pytest.raises(InvalidResponseError):
        result2 = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_and_get_invalid_responses()


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": "one",
            "What is your favorite animal?": [1, "bird", "dog"],
            "What is your favourite food?": "chocolate",
        }
    ],
)
def test_multiple_invalid_questionnaire_response_choices(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
    )
    questionnaire.add_question(
        name="What is your favorite animal?",
        choices=["dog", "cat", "pig"],
        multiple=True,
    )
    questionnaire.add_question(
        name="What is your favourite food?", choices=["chicken", "pasta", "rice"]
    )

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_choices()

    assert len(result) == 2
    with pytest.raises(InvalidResponseError):
        result2 = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_and_get_invalid_responses()


@pytest.mark.parametrize(
    "response",
    [
        {
            "How many years of experience do you have in programming?": 1,
            "What is your favorite animal?": ["cat", "dog"],
            "What is your favourite food?": "pasta",
        }
    ],
)
def test_multiple_invalid_questionnaire_response_rules(response: dict):
    questionnaire = Questionnaire(name="sample_questionaire", version=1)
    questionnaire.add_question(
        name="How many years of experience do you have in programming?",
        type=QuestionType.INT,
        validation_rules=["text", "number2"],
    )
    questionnaire.add_question(
        name="What is your favorite animal?",
        choices=["dog", "cat", "pig"],
        multiple=True,
    )
    questionnaire.add_question(
        name="What is your favourite food?",
        choices=["chicken", "pasta", "rice"],
        validation_rules=["number2"],
    )

    result = QuestionnaireResponseValidator(
        questionnaire=questionnaire, responses=response
    ).validate_questionnaire_responses_rules()
    assert len(result) == 2
    with pytest.raises(InvalidResponseError):
        result2 = QuestionnaireResponseValidator(
            questionnaire=questionnaire, responses=response
        ).validate_and_get_invalid_responses()
