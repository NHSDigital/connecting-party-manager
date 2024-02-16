from .questionnaire import Questionnaire


# You must bump the version if you edit this questionnaire
def create_spine_device_questionnaire_v1():
    spine_device_questionnaire = Questionnaire(name="spine_device", version=1)
    spine_device_questionnaire.add_question(
        name="ManufacturingOdsCode", answer_type=str
    )
    spine_device_questionnaire.add_question(
        name="InteractionIds", answer_type=str, mandatory=True, multiple=True
    )
    spine_device_questionnaire.add_question(name="Owner", answer_type=str)
    spine_device_questionnaire.add_question(name="PartyKey", answer_type=str)
    # nhsIDCode ods_code?

    return spine_device_questionnaire
