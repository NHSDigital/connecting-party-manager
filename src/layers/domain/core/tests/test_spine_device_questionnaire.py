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

    Q_nhs_mhs_manufacturer_org = Question(
        name="nhs_mhs_manufacturer_org",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_as_svc_ia = Question(
        name="nhs_as_svc_ia",
        answer_type=str,
        mandatory=True,
        multiple=True,
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

    Q_nhs_id_code = Question(
        name="nhs_id_code",
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
    Q_unique_identifier = Question(
        name="unique_identifier",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_as_client = Question(
        name="nhs_as_client",
        answer_type=str,
        mandatory=False,
        multiple=True,
        validation_rules=None,
        choices=None,
    )
    Q_object_class = Question(
        name="object_class",
        answer_type=str,
        mandatory=True,
        multiple=False,
        validation_rules=None,
        choices=["nhsas"],
    )
    Q_nhs_approver_urp = Question(
        name="nhs_approver_urp",
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
    Q_nhs_requestor_urp = Question(
        name="nhs_requestor_urp",
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
    Q_nhs_product_key = Question(
        name="nhs_product_key",
        answer_type=str,
        mandatory=True,
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
    Q_nhs_as_acf = Question(
        name="nhs_as_acf",
        answer_type=str,
        mandatory=False,
        multiple=True,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_temp_uid = Question(
        name="nhs_temp_uid",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_description = Question(
        name="description",
        answer_type=str,
        mandatory=False,
        multiple=False,
        validation_rules=None,
        choices=None,
    )
    Q_nhs_as_category_bag = Question(
        name="nhs_as_category_bag",
        answer_type=str,
        mandatory=False,
        multiple=True,
        validation_rules=None,
        choices=None,
    )

    assert Q_nhs_mhs_manufacturer_org.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_as_svc_ia.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_mhs_party_key.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_id_code.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_product_name.name in spine_device_questionnaire_v1.questions
    assert Q_unique_identifier.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_as_client.name in spine_device_questionnaire_v1.questions
    assert Q_object_class.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_approver_urp.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_date_approved.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_requestor_urp.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_date_requested.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_product_key.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_product_version.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_as_acf.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_temp_uid.name in spine_device_questionnaire_v1.questions
    assert Q_description.name in spine_device_questionnaire_v1.questions
    assert Q_nhs_as_category_bag.name in spine_device_questionnaire_v1.questions

    assert (
        Q_nhs_mhs_manufacturer_org
        == spine_device_questionnaire_v1.questions[Q_nhs_mhs_manufacturer_org.name]
    )
    assert (
        Q_nhs_as_svc_ia == spine_device_questionnaire_v1.questions[Q_nhs_as_svc_ia.name]
    )
    assert (
        Q_nhs_mhs_party_key
        == spine_device_questionnaire_v1.questions[Q_nhs_mhs_party_key.name]
    )
    assert Q_nhs_id_code == spine_device_questionnaire_v1.questions[Q_nhs_id_code.name]
    assert (
        Q_nhs_product_name
        == spine_device_questionnaire_v1.questions[Q_nhs_product_name.name]
    )

    assert (
        Q_unique_identifier
        == spine_device_questionnaire_v1.questions[Q_unique_identifier.name]
    )
    assert (
        Q_nhs_as_client == spine_device_questionnaire_v1.questions[Q_nhs_as_client.name]
    )

    assert (
        Q_object_class == spine_device_questionnaire_v1.questions[Q_object_class.name]
    )
    assert (
        Q_nhs_approver_urp
        == spine_device_questionnaire_v1.questions[Q_nhs_approver_urp.name]
    )
    assert (
        Q_nhs_date_approved
        == spine_device_questionnaire_v1.questions[Q_nhs_date_approved.name]
    )
    assert (
        Q_nhs_requestor_urp
        == spine_device_questionnaire_v1.questions[Q_nhs_requestor_urp.name]
    )
    assert (
        Q_nhs_date_requested
        == spine_device_questionnaire_v1.questions[Q_nhs_date_requested.name]
    )
    assert (
        Q_nhs_product_key
        == spine_device_questionnaire_v1.questions[Q_nhs_product_key.name]
    )
    assert (
        Q_nhs_product_version
        == spine_device_questionnaire_v1.questions[Q_nhs_product_version.name]
    )
    assert Q_nhs_as_acf == spine_device_questionnaire_v1.questions[Q_nhs_as_acf.name]
    assert (
        Q_nhs_temp_uid == spine_device_questionnaire_v1.questions[Q_nhs_temp_uid.name]
    )
    assert Q_description == spine_device_questionnaire_v1.questions[Q_description.name]
    assert (
        Q_nhs_as_category_bag
        == spine_device_questionnaire_v1.questions[Q_nhs_as_category_bag.name]
    )
