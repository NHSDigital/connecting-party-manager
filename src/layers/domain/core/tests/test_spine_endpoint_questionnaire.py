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
    assert spine_endpoint_questionnaire_v1.questions is not None

    Q_nhs_mhs_end_point = Question(
        name="nhs_mhs_end_point",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=[url],
        choices=None,
    )
    Q_unique_identifier = Question(
        name="unique_identifier",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_id_code = Question(
        name="nhs_id_code",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhsMhsFQDN = Question(
        name="nhsMhsFQDN",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_party_key = Question(
        name="nhs_mhs_party_key",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_cpa_id = Question(
        name="nhs_mhs_cpa_id",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhsMHSId = Question(
        name="nhsMHSId",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_actor = Question(
        name="nhs_mhs_actor",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=[
            "urn:oasis:names:tc:ebxml-msg:actor:topartymsh",
            "urn:oasis:names:tc:ebxml-msg:actor:nextmsh",
        ],
    )
    Q_nhs_mhs_sync_reply_mode = Question(
        name="nhs_mhs_sync_reply_mode",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=["MSHSIGNALSONLY", "NEVER", "NONE", "SIGNALSANDRESPONSE"],
    )
    Q_nhs_mhs_retry_interval = Question(
        name="nhs_mhs_retry_interval",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_retries = Question(
        name="nhs_mhs_retries",
        answer_type=(str, int),
        mandatory=False,
        multiple=False,
        validation_rules=[empty_str],
        choices=None,
    )
    Q_nhs_mhs_persist_duration = Question(
        name="nhs_mhs_persist_duration",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_duplicate_elimination = Question(
        name="nhs_mhs_duplicate_elimination",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=["ALWAYS", "NEVER"],
    )
    Q_nhs_mhs_ack_requested = Question(
        name="nhs_mhs_ack_requested",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=["ALWAYS", "NEVER"],
    )
    Q_nhs_mhs_svc_ia = Question(
        name="nhs_mhs_svc_ia",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_object_class = Question(
        name="object_class",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=["nhsmhs"],
    )
    Q_nhs_approver_urp = Question(
        name="nhs_approver_urp",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_contract_property_template_key = Question(
        name="nhs_contract_property_template_key",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_date_approved = Question(
        name="nhs_date_approved",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_date_dns_approved = Question(
        name="nhs_date_dns_approved",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_date_requested = Question(
        name="nhs_date_requested",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_dns_approver = Question(
        name="nhs_dns_approver",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_ep_interaction_type = Question(
        name="nhs_ep_interaction_type",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=["FHIR", "HL7", "EBXML", "N/A", "MSHSIGNALSONLY"],
    )
    Q_nhs_mhs_fqdn = Question(
        name="nhs_mhs_fqdn",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_in = Question(
        name="nhs_mhs_in",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_ip_address = Question(
        name="nhs_mhs_ip_address",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_is_authenticated = Question(
        name="nhs_mhs_is_authenticated",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=["NONE", "TRANSIENT", "PERSISTENT"],
    )
    Q_nhs_mhs_sn = Question(
        name="nhs_mhs_sn",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_product_key = Question(
        name="nhs_product_key",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_product_name = Question(
        name="nhs_product_name",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_product_version = Question(
        name="nhs_product_version",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_requestor_urp = Question(
        name="nhs_requestor_urp",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_mhs_service_description = Question(
        name="nhs_mhs_service_description",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )

    assert Q_nhs_mhs_end_point.name in spine_endpoint_questionnaire_v1.questions
    assert Q_unique_identifier.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_id_code.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhsMhsFQDN.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_party_key.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_cpa_id.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhsMHSId.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_actor.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_sync_reply_mode.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_retry_interval.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_retries.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_persist_duration.name in spine_endpoint_questionnaire_v1.questions
    assert (
        Q_nhs_mhs_duplicate_elimination.name
        in spine_endpoint_questionnaire_v1.questions
    )
    assert Q_nhs_mhs_ack_requested.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_svc_ia.name in spine_endpoint_questionnaire_v1.questions
    assert Q_object_class.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_approver_urp.name in spine_endpoint_questionnaire_v1.questions
    assert (
        Q_nhs_contract_property_template_key.name
        in spine_endpoint_questionnaire_v1.questions
    )
    assert Q_nhs_date_approved.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_date_dns_approved.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_date_requested.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_dns_approver.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_ep_interaction_type.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_fqdn.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_in.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_ip_address.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_is_authenticated.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_mhs_sn.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_product_key.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_product_name.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_product_version.name in spine_endpoint_questionnaire_v1.questions
    assert Q_nhs_requestor_urp.name in spine_endpoint_questionnaire_v1.questions
    assert (
        Q_nhs_mhs_service_description.name in spine_endpoint_questionnaire_v1.questions
    )

    assert (
        Q_nhs_mhs_end_point
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_end_point.name]
    )
    assert (
        Q_unique_identifier
        == spine_endpoint_questionnaire_v1.questions[Q_unique_identifier.name]
    )
    assert (
        Q_nhs_id_code == spine_endpoint_questionnaire_v1.questions[Q_nhs_id_code.name]
    )
    assert Q_nhsMhsFQDN == spine_endpoint_questionnaire_v1.questions[Q_nhsMhsFQDN.name]
    assert (
        Q_nhs_mhs_party_key
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_party_key.name]
    )
    assert (
        Q_nhs_mhs_cpa_id
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_cpa_id.name]
    )
    assert Q_nhsMHSId == spine_endpoint_questionnaire_v1.questions[Q_nhsMHSId.name]
    assert (
        Q_nhs_mhs_actor
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_actor.name]
    )
    assert (
        Q_nhs_mhs_sync_reply_mode
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_sync_reply_mode.name]
    )
    assert (
        Q_nhs_mhs_retry_interval
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_retry_interval.name]
    )
    assert (
        Q_nhs_mhs_retries
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_retries.name]
    )
    assert (
        Q_nhs_mhs_persist_duration
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_persist_duration.name]
    )
    assert (
        Q_nhs_mhs_duplicate_elimination
        == spine_endpoint_questionnaire_v1.questions[
            Q_nhs_mhs_duplicate_elimination.name
        ]
    )
    assert (
        Q_nhs_mhs_ack_requested
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_ack_requested.name]
    )
    assert (
        Q_nhs_mhs_svc_ia
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_svc_ia.name]
    )
    assert (
        Q_object_class == spine_endpoint_questionnaire_v1.questions[Q_object_class.name]
    )
    assert (
        Q_nhs_approver_urp
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_approver_urp.name]
    )
    assert (
        Q_nhs_contract_property_template_key
        == spine_endpoint_questionnaire_v1.questions[
            Q_nhs_contract_property_template_key.name
        ]
    )
    assert (
        Q_nhs_date_approved
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_date_approved.name]
    )
    assert (
        Q_nhs_date_dns_approved
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_date_dns_approved.name]
    )
    assert (
        Q_nhs_date_requested
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_date_requested.name]
    )
    assert (
        Q_nhs_dns_approver
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_dns_approver.name]
    )
    assert (
        Q_nhs_ep_interaction_type
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_ep_interaction_type.name]
    )
    assert (
        Q_nhs_mhs_fqdn == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_fqdn.name]
    )
    assert Q_nhs_mhs_in == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_in.name]
    assert (
        Q_nhs_mhs_ip_address
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_ip_address.name]
    )
    assert (
        Q_nhs_mhs_is_authenticated
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_is_authenticated.name]
    )
    assert Q_nhs_mhs_sn == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_sn.name]
    assert (
        Q_nhs_product_key
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_product_key.name]
    )
    assert (
        Q_nhs_product_name
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_product_name.name]
    )
    assert (
        Q_nhs_product_version
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_product_version.name]
    )
    assert (
        Q_nhs_requestor_urp
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_requestor_urp.name]
    )
    assert (
        Q_nhs_mhs_service_description
        == spine_endpoint_questionnaire_v1.questions[Q_nhs_mhs_service_description.name]
    )
