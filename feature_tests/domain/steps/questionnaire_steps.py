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


@when("I create a Questionnaire with the following attributes")
def when_create_questionnaire(context: Context):
    for row in context.table:
        questionnaire_name = row["name"]
        questionnaire_version = int(row["version"])

        q = Questionnaire(name=questionnaire_name, version=questionnaire_version)
        context.questionnaires[(questionnaire_name, questionnaire_version)] = q


@then("a questionnaire with the following attributes is created")
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


@when("I add the following questions to Questionnaire {name} version {version}")
def step_impl(context: Context, name, version):
    subject = context.questionnaires[(name, version)]
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        multiple = row["multiple"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        subject.add_question(
            name=question_name, answer_type=answer_type, multiple=multiple
        )


@then("Questionnaire {name} version {version} has the questions")
def step_impl(context: Context, name, version):
    subject = context.questionnaires[(name, version)]
    assert subject.name == name
    ix = 0
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        multiple = row["multiple"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        q = subject.questions[question_name]
        assert q is not None
        assert q.answer_type == answer_type
        assert q.multiple == multiple

        ix = ix + 1
    assert len(subject.questions) == ix


@given("the following questions in Questionnaire {name} version {version}")
def given_questionnaire(context: Context, name: str, version: int):
    q = Questionnaire(name=name, version=version)
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        multiple = row["multiple"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        q.add_question(name=question_name, answer_type=answer_type, multiple=multiple)
    context.questionnaires[(name, version)] = q


@when(
    "the following questionnaire responses are provided to Questionnaire {name} version {version}"
)
def when_questionnaire_responses_provided(context: Context, name: str, version: int):
    context.questionnaire_response = []
    # questionnaire_name = name
    # questionnaire_version = version
    for row in context.table:
        question_name = row["question"]
        answer = row["answer"]
        question_type = (
            context.questionnaires[(name, version)].questions[question_name].answer_type
        )

        if question_type == str:
            answer = str(answer)
        elif question_type == int:
            answer = int(answer)
        elif question_type == bool:
            answer = bool(answer)
        elif question_type == datetime:
            answer = datetime.strptime(answer, "%Y-%m-%d %H:%M:%S")
        elif question_type == float:
            answer = float(answer)
        elif question_type == date:
            answer = datetime.strptime(answer, "%Y-%m-%d").date()
        elif question_type == time:
            answer = datetime.strptime(answer, "%H:%M:%S").time()

        context.questionnaire_response.append((question_name, [answer]))

    assert len(context.questionnaire_response) != 0


@then(
    "the questionnaire responses are validated successfully against Questionnaire {name} version {version}"
)
def validate_responses(context: Context, name: str, version: int):
    questionnaire_answered = context.questionnaires[(name, version)]
    responses = context.questionnaire_response

    QuestionnaireResponse(questionnaire=questionnaire_answered, responses=responses)
    # Assert anything?


@when("I try to create a Questionnaire without a name attribute")
def when_try_to_create_questionnaire_missing_name(context: Context):
    try:
        for row in context.table:
            questionnaire_version = int(row["version"])

            q = Questionnaire(version=questionnaire_version)
    except ValidationError as e:
        context.error = str(e)


@then("the result for missing name is error ValidationError")
def then_result_is_error(context: Context):
    assert context.error is not None
    assert "validation error" in context.error.lower()
    assert "name" in context.error.lower()
    assert "field required" in context.error.lower()


@when("I try to create a Questionnaire without a version attribute")
def when_try_to_create_questionnaire(context: Context):
    try:
        for row in context.table:
            questionnaire_name = row["name"]

            q = Questionnaire(name=questionnaire_name)
    except ValidationError as e:
        context.error = str(e)


@then("the result for missing version is error ValidationError")
def then_result_is_error(context: Context):
    assert context.error is not None
    assert "validation error" in context.error.lower()
    assert "version" in context.error.lower()
    assert "field required" in context.error.lower()


@when("I try to add an invalid question to Questionnaire {name} version {version}")
def add_invalid_question(context: Context, name: str, version: int):
    q = context.questionnaires[(name, version)]

    try:
        q.add_question()
    except TypeError as e:
        context.error = str(e)


@then("the result is TypeError for missing question name")
def then_result_is_error(context: Context):
    assert context.error is not None
    assert "missing 1 required positional argument: 'name'" in context.error.lower()


@then(
    "the questionnaire responses fail validation against the Questionnaire {name} version {version}"
)
def validate_responses(context: Context, name: str, version: int):
    questionnaire_answered = context.questionnaires[(name, version)]
    responses = context.questionnaire_response

    try:
        QuestionnaireResponse(questionnaire=questionnaire_answered, responses=responses)
    except ValidationError as e:
        context.error = str(e)


@when(
    "I try to add the following duplicate questions to Questionnaire {name} version {version}"
)
def step_impl(context: Context, name, version):
    subject = context.questionnaires[(name, version)]
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        multiple = row["multiple"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        try:
            subject.add_question(
                name=question_name, answer_type=answer_type, multiple=multiple
            )
        except DuplicateError as e:
            context.error = str(e)


@then("the result for duplicate questions is error DuplicateError")
def then_result_is_error(context: Context):
    assert context.error is not None
    assert "question" in context.error.lower()
    assert "already exists" in context.error.lower()
