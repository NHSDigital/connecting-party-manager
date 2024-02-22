from .questionnaire import Questionnaire
from .questionnaire_validation_custom_rules import url


# You must bump the version if you edit this questionnaire
def create_spine_endpoint_questionnaire_v1():
    spine_endpoint_questionnaire = Questionnaire(name="spine_endpoint", version=1)
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_end_point",
        answer_type=str,
        mandatory=True,
        validation_rules=[url],
    )  # This is the address
    spine_endpoint_questionnaire.add_question(
        name="unique_identifier", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhs_id_code", answer_type=str, mandatory=True
    )  # This is the managingOrganization
    spine_endpoint_questionnaire.add_question(
        name="nhsMhsFQDN", answer_type=str, mandatory=True
    )  # not in Joel's model
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_party_key", answer_type=str, mandatory=True
    )  # Red in Joel's model
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_cpa_id", answer_type=str, mandatory=True
    )
    spine_endpoint_questionnaire.add_question(
        name="nhsMHSId", answer_type=str, mandatory=True
    )  # not in Joel's model
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_actor",
        answer_type=str,
        choices=[
            "urn:oasis:names:tc:ebxml-msg:actor:topartymsh",
            "urn:oasis:names:tc:ebxml-msg:actor:nextmsh",
        ],
    )  # This is the reliabilityConfigurationActor - ticket mandatory, Joel optional
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_sync_reply_mode",
        answer_type=str,
        choices=["MSHSIGNALSONLY", "NEVER", "NONE", "SIGNALSANDRESPONSE"],
    )  # This is the reliabilityConfigurationReplyMode - mandatory on ticket? Optional for Joel
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_retry_interval", answer_type=str
    )  # This is the reliabilityConfigurationRetryInterval - mandatory on ticket, optional Joel
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_retries", answer_type=str
    )  # This is the reliabilityConfigurationRetries - mandatory on ticket, optional Joel
    # str or int, empty if str  ???
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_persist_duration", answer_type=str
    )  # This is the reliabilityConfigurationPersistDuration - ticket mandatory, Joel optional
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_duplicate_elimination",
        answer_type=str,
        choices=["ALWAYS", "NEVER"],
    )  # This is the reliabilityConfigurationDuplicationElimination - optional?
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_ack_requested", answer_type=str, choices=["ALWAYS", "NEVER"]
    )  # This is the reliabilityConfigurationAckRequested - optional?
    spine_endpoint_questionnaire.add_question(
        name="nhs_mhs_svc_ia", answer_type=str
    )  # This is the interactionID - red in joel's model

    # not on ticket:
    spine_endpoint_questionnaire.add_question(
        name="object_class", answer_type=str, mandatory=True, choices=["nhsmhs"]
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
        choices=["FHIR", "HL7", "EBXML", "N/A", "MSHSIGNALSONLY"],
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
        choices=["NONE", "TRANSIENT", "PERSISTENT"],
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
