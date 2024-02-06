from behave import given, then, when
from domain.core.questionnaire import Questionnaire

from feature_tests.domain.steps.context import Context


@given("Questionnaire {name} version {version}")
def given__questionnaire(context: Context, name: str, version: int):
    q = Questionnaire(name=name, version=version)
    context.questionnaires[name] = q


@when("I add the following questions to {name}")
def step_impl(context: Context, name):
    subject = context.questionnaires[name]
    for row in context.table:
        question_name = row["name"]
        answer_type = row["type"]
        multiple = row["multiple"].lower() == "true"

        subject.add_question(question_name, answer_type=answer_type, multiple=multiple)


@then("Questionnaire {name} version {version} has the questions")
def step_impl(context: Context, name, version):
    subject = context.questionnaires[name]
    ix = 0
    for row in context.table:
        question_name = row["name"]
        answer_type = row["type"]
        multiple = row["multiple"].lower() == "true"

        q = subject.questions[question_name]
        assert q is not None, "question exists"
        assert q.answer_type == answer_type, "question answer_type"
        assert q.multiple == multiple, "question multiple"

        ix = ix + 1
    assert len(subject.questions) == ix, "count"
