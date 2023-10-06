import pytest
from domain.core.error import DuplicateError
from domain.core.questionnaire_entity import Dataset, QuestionnaireEntity


class TestQuestionnaireEntity(QuestionnaireEntity):
    __test__ = False


def test_constructor():
    subject = TestQuestionnaireEntity()

    assert subject._datasets is not None, "datasets"


@pytest.mark.parametrize(
    ["index"],
    [
        ["alpha"],
        ["beta"],
        ["gamma"],
    ],
)
def test_add_dataset(index: str):
    subject = TestQuestionnaireEntity()

    result = subject.add_dataset(index)

    assert result is not None, "Result returned"
    assert result._values is not None, "Result has values"
    assert isinstance(result, Dataset), "Is dataset"
    assert index in subject._datasets, "Index added"
    assert result == subject._datasets[index], "Dataset is at index"


@pytest.mark.parametrize(
    ["index"],
    [
        ["alpha"],
        ["beta"],
        ["gamma"],
    ],
)
def test_cannot_add_duplicate_dataset(index: str):
    subject = TestQuestionnaireEntity()

    subject.add_dataset(index)
    with pytest.raises(DuplicateError):
        subject.add_dataset(index)
