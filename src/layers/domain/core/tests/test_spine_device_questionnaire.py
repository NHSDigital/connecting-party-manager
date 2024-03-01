import pytest
from domain.core.load_questionnaire import render_questionnaire
from domain.core.questionnaire import Question


@pytest.mark.parametrize(
    ["name", "version"],
    [["spine_device", 1]],
)
def test_spine_device_questionnaire_v1(name: str, version: int):
    spine_device_questionnaire_v1 = render_questionnaire(
        questionnaire_name=name, questionnaire_version=version
    )

    assert spine_device_questionnaire_v1 is not None
    assert spine_device_questionnaire_v1.name == name
    assert spine_device_questionnaire_v1.version == version

    EXPECTED_QUESTIONS = [
        Question(
            name="nhs_mhs_manufacturer_org",
            human_readable_name="Manufacturer Ods Code",
            answer_types={str},
            mandatory=False,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_as_svc_ia",
            human_readable_name="Interaction Ids",
            answer_types={str},
            mandatory=True,
            multiple=True,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_mhs_party_key",
            human_readable_name="Party Key",
            answer_types={str},
            mandatory=True,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_id_code",
            human_readable_name="Owner",
            answer_types={str},
            mandatory=True,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_product_name",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="unique_identifier",
            human_readable_name="ASID",
            answer_types={str},
            mandatory=True,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_as_client",
            answer_types={str},
            human_readable_name="Owner",
            mandatory=False,
            multiple=True,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="object_class",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices={"nhsas"},
        ),
        Question(
            name="nhs_approver_urp",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_date_approved",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_requestor_urp",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_date_requested",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_product_key",
            answer_types={str},
            mandatory=True,
            human_readable_name="",
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_product_version",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_as_acf",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=True,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_temp_uid",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="description",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=False,
            validation_rules=set(),
            choices=set(),
        ),
        Question(
            name="nhs_as_category_bag",
            answer_types={str},
            human_readable_name="",
            mandatory=False,
            multiple=True,
            validation_rules=set(),
            choices=set(),
        ),
    ]

    assert len(EXPECTED_QUESTIONS) == len(spine_device_questionnaire_v1.questions)

    for expected_question in EXPECTED_QUESTIONS:
        actual_question = spine_device_questionnaire_v1.questions[
            expected_question.name
        ]

        assert expected_question == actual_question
