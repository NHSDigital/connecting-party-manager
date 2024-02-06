from datetime import date, datetime, time

from behave import given, then, when
from domain.core.questionnaire import Questionnaire

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


@given("Questionnaire {name} version {version}")
def given__questionnaire(context: Context, name: str, version: int):
    q = Questionnaire(name=name, version=version)
    context.questionnaires[(name, version)] = q


@when("I add the following questions to {name} version {version}")
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
    ix = 0
    for row in context.table:
        question_name = row["name"]
        answer_type_str = row["type"]
        multiple = row["multiple"].lower() == "true"

        # Convert the string to the corresponding Python type
        answer_type = TYPE_MAPPING.get(answer_type_str.lower())

        q = subject.questions[question_name]
        assert q is not None, "question exists"
        assert q.answer_type == answer_type, "question answer_type"
        assert q.multiple == multiple, "question multiple"

        ix = ix + 1
    assert len(subject.questions) == ix, "count"
