from .questionnaire import Questionnaire


# You must bump the version if you edit this questionnaire
def create_spine_device_questionnaire_v1():
    spine_device_questionnaire = Questionnaire(name="spine_device", version=1)
    spine_device_questionnaire.add_question(
        name="nhs_mhs_manufacturer_org", answer_type=str
    )  # This is the ManufacturingOdsCode
    spine_device_questionnaire.add_question(
        name="nhs_as_svc_ia", answer_type=str, mandatory=True, multiple=True
    )  # These are the InteractionIds
    spine_device_questionnaire.add_question(
        name="nhs_mhs_party_key", answer_type=str, mandatory=True
    )

    spine_device_questionnaire.add_question(
        name="nhs_id_code", answer_type=str, mandatory=True
    )  # What is this? Different to nhs_as_client
    spine_device_questionnaire.add_question(name="nhs_product_name", answer_type=str)
    # covered in cpm device class but may need to override?

    spine_device_questionnaire.add_question(
        name="unique_identifier", answer_type=str, mandatory=True
    )  # This is the ASID
    spine_device_questionnaire.add_question(
        name="nhs_as_client", answer_type=str, multiple=True
    )
    spine_device_questionnaire.add_question(
        name="object_class", answer_type=str, mandatory=True, choices=["nhsas"]
    )
    spine_device_questionnaire.add_question(
        name="nhs_approver_urp", answer_type=str, mandatory=True
    )
    spine_device_questionnaire.add_question(
        name="nhs_date_approved", answer_type=str, mandatory=True
    )
    spine_device_questionnaire.add_question(
        name="nhs_requestor_urp", answer_type=str, mandatory=True
    )
    spine_device_questionnaire.add_question(
        name="nhs_date_requested", answer_type=str, mandatory=True
    )
    spine_device_questionnaire.add_question(
        name="nhs_product_key", answer_type=str, mandatory=True
    )
    spine_device_questionnaire.add_question(name="nhs_product_version", answer_type=str)
    spine_device_questionnaire.add_question(
        name="nhs_as_acf", answer_type=str, multiple=True
    )
    spine_device_questionnaire.add_question(name="nhs_temp_uid", answer_type=str)
    spine_device_questionnaire.add_question(name="description", answer_type=str)
    spine_device_questionnaire.add_question(
        name="nhs_as_category_bag", answer_type=str, multiple=True
    )

    return spine_device_questionnaire
