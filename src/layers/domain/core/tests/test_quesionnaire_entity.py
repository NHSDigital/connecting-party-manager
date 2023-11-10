from uuid import UUID

import pytest
from domain.core.questionnaire_entity import Dataset, QuestionnaireEntity


class TestQuestionnaireEntity(QuestionnaireEntity):
    __test__ = False


def test_constructor():
    subject = TestQuestionnaireEntity(
        id="0cd24369-a9b5-4cbc-8a2a-0f9031fd8fb4", name="Test"
    )

    assert subject._datasets is not None, "datasets"


@pytest.mark.parametrize(
    ["index"],
    [
        ["alpha"],
        ["beta"],
        ["gamma"],
    ],
)
def test__add_dataset(index: str):
    subject = TestQuestionnaireEntity(
        id=UUID("5e9041aa-44a6-4778-9ba6-acbf5aa1b06a"), name="test"
    )

    result = subject.add_dataset(index)

    assert result is not None, "Result returned"
    assert result._values is not None, "Result has values"
    assert isinstance(result, Dataset), "Is dataset"
    assert index in subject._datasets, "Index added"
    assert result == subject._datasets[index], "Dataset is at index"
