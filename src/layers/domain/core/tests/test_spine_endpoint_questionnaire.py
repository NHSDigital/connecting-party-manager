import pytest
from domain.core.questionnaire import Question
from domain.core.questionnaire_validation_custom_rules import empty_str, url
from domain.core.spine_endpoint_questionnaire import (
    create_spine_endpoint_questionnaire_v1,
)


@pytest.mark.parametrize(
    ["name", "version"],
    [["spine_endpoint", 1]],
)
def test_spine_endpoint_questionnaire_v1(name: str, version: int):
    spine_endpoint_questionnaire_v1 = create_spine_endpoint_questionnaire_v1()

    assert spine_endpoint_questionnaire_v1 is not None
    assert spine_endpoint_questionnaire_v1.name == name
    assert spine_endpoint_questionnaire_v1.version == version

    EXPECTED_QUESTIONS = [
        Question(
            name="nhs_mhs_end_point",
            human_readable_name="This is the address",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules={url},
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
            name="nhs_id_code",
            human_readable_name="This is the Managing Organization",
            answer_type=str,
            mandatory=True,
            multiple=False,
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
            name="nhs_mhs_cpa_id",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_actor",
            human_readable_name="This is the Reliability Configuration Actor",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices={
                "urn:oasis:names:tc:ebxml-msg:actor:topartymsh",
                "urn:oasis:names:tc:ebxml-msg:actor:nextmsh",
            },
        ),
        Question(
            name="nhs_mhs_sync_reply_mode",
            human_readable_name="This is the Reliability Configuration Reply Mode",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices={"MSHSIGNALSONLY", "NEVER", "NONE", "SIGNALSANDRESPONSE"},
        ),
        Question(
            name="nhs_mhs_retry_interval",
            human_readable_name="This is the Reliability Configuration Retry Interval",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_retries",
            human_readable_name="This is the Reliability Configuration Retries",
            answer_type=(str, int),
            mandatory=False,
            multiple=False,
            validation_rules={empty_str},
            choices=None,
        ),
        Question(
            name="nhs_mhs_persist_duration",
            human_readable_name="This is the Reliability Configuration Persist Duration",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_duplicate_elimination",
            human_readable_name="This is the Reliability Configuration Duplication Elimination",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices={"ALWAYS", "NEVER"},
        ),
        Question(
            name="nhs_mhs_ack_requested",
            human_readable_name="This is the Reliability Configuration Ack Requested",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices={"ALWAYS", "NEVER"},
        ),
        Question(
            name="nhs_mhs_svc_ia",
            human_readable_name="This is the interaction ID",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="object_class",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices={"nhsmhs"},
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
            name="nhs_contract_property_template_key",
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
            name="nhs_date_dns_approved",
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
            name="nhs_dns_approver",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_ep_interaction_type",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices={"FHIR", "HL7", "EBXML", "N/A", "MSHSIGNALSONLY"},
        ),
        Question(
            name="nhs_mhs_fqdn",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_in",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_ip_address",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_is_authenticated",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices={"NONE", "TRANSIENT", "PERSISTENT"},
        ),
        Question(
            name="nhs_mhs_sn",
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
            name="nhs_product_name",
            answer_type=str,
            mandatory=False,
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
            name="nhs_requestor_urp",
            answer_type=str,
            mandatory=True,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
        Question(
            name="nhs_mhs_service_description",
            answer_type=str,
            mandatory=False,
            multiple=False,
            validation_rules=None,
            choices=None,
        ),
    ]

    assert len(EXPECTED_QUESTIONS) == len(spine_endpoint_questionnaire_v1.questions)

    for expected_question in EXPECTED_QUESTIONS:
        actual_question = spine_endpoint_questionnaire_v1.questions[
            expected_question.name
        ]

        assert expected_question == actual_question
