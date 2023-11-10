import uuid

from behave import given, then, when
from domain.core.questionnaire import Questionnaire, QuestionType

from feature_tests.steps.context import Context


@given("Questionnaire {id}")
def given__questionnaire(context: Context, id: str):
    q = Questionnaire(id=uuid.uuid4(), name=id)
    context.questionnaires[id] = q


@when("I add the following questions to {id}")
def step_impl(context: Context, id):
    subject = context.questionnaires[id]
    for row in context.table:
        name = row["name"]
        qtype = QuestionType[row["type"]]
        multiple = row["multiple"].lower() == "true"

        subject.add_question(name, type=qtype, multiple=multiple)


@then("Questionnaire {id} has the questions")
def step_impl(context: Context, id):
    subject = context.questionnaires[id]
    ix = 0
    for row in context.table:
        question_type = QuestionType[row["type"]]
        multiple = row["multiple"].lower() == "true"

        q = subject._questions[ix]
        assert q is not None, "question exists"
        assert q.type == question_type, "question type"
        assert q.multiple == multiple, "question multiple"

        ix = ix + 1
    assert len(subject._questions) == ix, "count"
