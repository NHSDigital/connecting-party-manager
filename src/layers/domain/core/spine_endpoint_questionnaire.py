from .questionnaire import Questionnaire
from .questionnaire_validation_custom_rules import empty_str, url


# You must bump the version if you edit this questionnaire
def create_spine_endpoint_questionnaire_v1():
    spine_endpoint_questionnaire = Questionnaire(name="spine_endpoint", version=1)
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_end_point",
        human_readable_name="This is the address",
        answer_type=str,
        mandatory=True,
        validation_rules={url},
    )
    spine_endpoint_questionnaire.add_question(
        name="unique_identifier",
        human_readable_name="This is the ASID",
        answer_type=str,
        mandatory=True,
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_id_code",
        human_readable_name="This is the Managing Organization",
        answer_type=str,
        mandatory=True,
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_party_key", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_cpa_id", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhsMHSId", answer_type=str, mandatory=True
    )  # not in Joel's model or nhs_mhs.py model
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_actor",
        human_readable_name="This is the Reliability Configuration Actor",
        answer_type=str,
        choices={
            "urn:oasis:names:tc:ebxml-msg:actor:topartymsh",
            "urn:oasis:names:tc:ebxml-msg:actor:nextmsh",
        },
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_sync_reply_mode",
        human_readable_name="This is the Reliability Configuration Reply Mode",
        answer_type=str,
        choices={"MSHSIGNALSONLY", "NEVER", "NONE", "SIGNALSANDRESPONSE"},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_retry_interval",
        human_readable_name="This is the Reliability Configuration Retry Interval",
        answer_type=str,
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_retries",
        human_readable_name="This is the Reliability Configuration Retries",
        answer_type=(str, int),
        validation_rules={empty_str},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_persist_duration",
        human_readable_name="This is the Reliability Configuration Persist Duration",
        answer_type=str,
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_duplicate_elimination",
        human_readable_name="This is the Reliability Configuration Duplication Elimination",
        answer_type=str,
        choices={"ALWAYS", "NEVER"},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_ack_requested",
        human_readable_name="This is the Reliability Configuration Ack Requested",
        answer_type=str,
        choices={"ALWAYS", "NEVER"},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_svc_ia",
        human_readable_name="This is the interaction ID",
        answer_type=str,
    )
    spine_endpoint_questionnaire.add_question(
        name="object_class", answer_type=str, mandatory=True, choices={"nhsmhs"}
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_approver_urp", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_contract_property_template_key", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_date_approved", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_date_dns_approved", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_date_requested", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_dns_approver", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_ep_interaction_type",
        answer_type=str,
        mandatory=True,
        choices={"FHIR", "HL7", "EBXML", "N/A", "MSHSIGNALSONLY"},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_fqdn", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_in", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_ip_address", answer_type=str
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_is_authenticated",
        answer_type=str,
        mandatory=True,
        choices={"NONE", "TRANSIENT", "PERSISTENT"},
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_sn", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_product_key", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(name="nhs_product_name", answer_type=str)
    spine_endpoint_questionnaire.add_question(
        name="nhs_product_version",
        answer_type=str,
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_requestor_urp", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_service_description",
        answer_type=str,
    )

    return spine_endpoint_questionnaire
