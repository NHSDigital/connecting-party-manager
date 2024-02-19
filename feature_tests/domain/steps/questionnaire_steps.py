from datetime import date, datetime, time

from behave import given, then, when
from domain.core.error import DuplicateError
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from pydantic import ValidationError

from feature_tests.domain.steps.context import Context

TYPE_MAPPING = {
    "str": str,
    "int": int,
    "bool": bool,
    "datetime": datetime,
    "float": float,
    "date": date,
    "time": time,
}


@when("the user creates a Questionnaire with the following attributes")
def when_create_questionnaire(context: Context):
    for row in context.table:
        try:
            questionnaire_name = row["name"]
            questionnaire_version = int(row["version"])
            q = Questionnaire(name=questionnaire_name, version=questionnaire_version)
            context.questionnaires[(questionnaire_name, questionnaire_version)] = q
        except (ValidationError, ValueError) as e:
            context.error = e


@then("the result is a Questionnaire with the following attributes")
def then_result_is_questionnaire_with(context: Context):
    for row in context.table:
        expected_name = row["expected_name"]
        expected_version = int(row["expected_version"])

        created_questionnaire = context.questionnaires[
            (expected_name, expected_version)
        ]

        assert created_questionnaire.name == expected_name
        assert created_questionnaire.version == expected_version


@given("Questionnaire {name} version {version}")
def given_questionnaire(context: Context, name: str, version: int):
    q = Questionnaire(name=name, version=version)
    context.questionnaires[(name, version)] = q


@when("the user adds the following Questions to Questionnaire {name} version {version}")
def step_impl(context: Context, name, version):
    subject = context.questionnaires[(name, version)]
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        mandatory = row["mandatory"].lower() == "true"
        try:
            answer_type = TYPE_MAPPING.get(answer_type_str.lower())
            subject.add_question(
                name=question_name, answer_type=answer_type, mandatory=mandatory
            )
        except (ValidationError, ValueError, DuplicateError) as e:
            context.error = e


@then("Questionnaire {name} version {version} has the questions")
def step_impl(context: Context, name, version):
    subject = context.questionnaires[(name, version)]
    assert subject.name == name
    ix = 0
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        mandatory = row["mandatory"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        q = subject.questions[question_name]
        assert q is not None
        assert q.answer_type == answer_type
        assert q.mandatory == mandatory

        ix = ix + 1
    assert len(subject.questions) == ix


@given("the following questions in Questionnaire {name} version {version}")
def given_questionnaire(context: Context, name: str, version: int):
    q = Questionnaire(name=name, version=version)

    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        mandatory = row["mandatory"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())
        q.add_question(name=question_name, answer_type=answer_type, mandatory=mandatory)
    context.questionnaires[(name, version)] = q


@when(
    "the following questionnaire responses are provided to Questionnaire {name} version {version}"
)
def when_questionnaire_responses_provided(context: Context, name: str, version: int):
    context.questionnaire_response = []
    for row in context.table:
        question_name = row["question"]
        answer = row["answer"]
        answer_type = row["answer_type"]

        if answer_type == "str":
            answer = str(answer)
        elif answer_type == "int":
            answer = int(answer)
        elif answer_type == "bool":
            if answer.lower() == "true" or answer.lower() == "false":
                answer = bool(answer)
            else:
                raise ValidationError(
                    f"answer type for question '{question_name}' must be bool"
                )
        elif answer_type == "datetime":
            answer = datetime.strptime(answer, "%Y-%m-%d %H:%M:%S")
        elif answer_type == "float":
            answer = float(answer)
        elif answer_type == "date":
            answer = datetime.strptime(answer, "%Y-%m-%d").date()
        elif answer_type == "time":
            answer = datetime.strptime(answer, "%H:%M:%S").time()

        context.questionnaire_response.append((question_name, [answer]))

    assert len(context.questionnaire_response) != 0


@when("the responses are validated against Questionnaire {name} version {version}")
def validate_responses(context: Context, name: str, version: int):
    questionnaire_answered = context.questionnaires[(name, version)]
    responses = context.questionnaire_response
    try:
        QuestionnaireResponse(questionnaire=questionnaire_answered, responses=responses)
    except (ValidationError, ValueError) as e:
        context.error = e
