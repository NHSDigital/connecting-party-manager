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

    EXPECTED_QUESTIONS = [
        Question(
            name="nhs_mhs_manufacturer_org",
            human_readable_name="This is the Manufacturer Ods Code",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_as_svc_ia",
            human_readable_name="These are the Interaction Ids",
            answer_type=str,
            mandatory=True,
            multiple=True,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_party_key",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_id_code",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_product_name",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="unique_identifier",
            human_readable_name="This is the ASID",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_as_client",
            answer_type=str,
            mandatory=False,
            multiple=True,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="object_class",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=["nhsas"],
        ),
        Question(
            name="nhs_approver_urp",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_date_approved",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_requestor_urp",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_date_requested",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_product_key",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_product_version",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_as_acf",
            answer_type=str,
            mandatory=False,
            multiple=True,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_temp_uid",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="description",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_as_category_bag",
            answer_type=str,
            mandatory=False,
            multiple=True,
            validation_rules=None,
            choices=None,
        ),
    ]

    assert len(EXPECTED_QUESTIONS) == len(spine_device_questionnaire_v1.questions)

    for expected_question in EXPECTED_QUESTIONS:
        actual_question = spine_device_questionnaire_v1.questions[
            expected_question.name
        ]

        assert expected_question == actual_question
