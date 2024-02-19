import pytest
from domain.core.questionnaire import Question
from domain.core.spine_device_questionnaire import create_spine_device_questionnaire_v1


@pytest.mark.parametrize(
    ["name", "version"],
    [["spine_device", 1]],
)
def test_spine_device_questionnaire_v1(name: str, version: int):
    spine_device_questionnaire_v1 = create_spine_device_questionnaire_v1()

    assert spine_device_questionnaire_v1 is not None
    assert spine_device_questionnaire_v1.name == name
    assert spine_device_questionnaire_v1.version == version
    assert spine_device_questionnaire_v1.questions is not None

    Q1 = Question(
        name="object_class",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=["nhsas"],
    )
    Q2 = Question(
        name="nhs_approver_urp",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q3 = Question(
        name="nhs_date_approved",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q4 = Question(
        name="nhs_requestor_urp",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q5 = Question(
        name="nhs_date_requested",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q6 = Question(
        name="nhs_id_code",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q7 = Question(
        name="nhs_mhs_manufacturer_org",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q8 = Question(
        name="nhs_mhs_party_key",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q9 = Question(
        name="nhs_product_key",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q10 = Question(
        name="nhs_product_name",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q11 = Question(
        name="nhs_product_version",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q12 = Question(
        name="nhs_as_acf",
        answer_type=str,
        mandatory=False,
        multiple=True,
        validation_rules=None,
        choices=None,
    )
    Q13 = Question(
        name="nhs_as_svc_ia",
        answer_type=str,
        mandatory=True,
        multiple=True,
        validation_rules=None,
        choices=None,
    )
    Q14 = Question(
        name="nhs_temp_uid",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q15 = Question(
        name="description",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q16 = Question(
        name="nhs_as_category_bag",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )

    assert Q1.name in spine_device_questionnaire_v1.questions
    assert Q2.name in spine_device_questionnaire_v1.questions
    assert Q3.name in spine_device_questionnaire_v1.questions
    assert Q4.name in spine_device_questionnaire_v1.questions
    assert Q5.name in spine_device_questionnaire_v1.questions
    assert Q6.name in spine_device_questionnaire_v1.questions
    assert Q7.name in spine_device_questionnaire_v1.questions
    assert Q8.name in spine_device_questionnaire_v1.questions
    assert Q9.name in spine_device_questionnaire_v1.questions
    assert Q10.name in spine_device_questionnaire_v1.questions
    assert Q11.name in spine_device_questionnaire_v1.questions
    assert Q12.name in spine_device_questionnaire_v1.questions
    assert Q13.name in spine_device_questionnaire_v1.questions
    assert Q14.name in spine_device_questionnaire_v1.questions
    assert Q15.name in spine_device_questionnaire_v1.questions
    assert Q16.name in spine_device_questionnaire_v1.questions

    assert Q1 == spine_device_questionnaire_v1.questions[Q1.name]
    assert Q2 == spine_device_questionnaire_v1.questions[Q2.name]
    assert Q3 == spine_device_questionnaire_v1.questions[Q3.name]
    assert Q4 == spine_device_questionnaire_v1.questions[Q4.name]
    assert Q5 == spine_device_questionnaire_v1.questions[Q5.name]
    assert Q6 == spine_device_questionnaire_v1.questions[Q6.name]
    assert Q7 == spine_device_questionnaire_v1.questions[Q7.name]
    assert Q8 == spine_device_questionnaire_v1.questions[Q8.name]
    assert Q9 == spine_device_questionnaire_v1.questions[Q9.name]
    assert Q10 == spine_device_questionnaire_v1.questions[Q10.name]
    assert Q11 == spine_device_questionnaire_v1.questions[Q11.name]
    assert Q12 == spine_device_questionnaire_v1.questions[Q12.name]
    assert Q13 == spine_device_questionnaire_v1.questions[Q13.name]
    assert Q14 == spine_device_questionnaire_v1.questions[Q14.name]
    assert Q15 == spine_device_questionnaire_v1.questions[Q15.name]
    assert Q16 == spine_device_questionnaire_v1.questions[Q16.name]
