from domain.core.device import Device
from domain.core.questionnaire import QuestionnaireResponse
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

from ..utils import update_in_list_of_dict


class DeletionErrorBase(Exception):
    def __init__(self, field):
        super().__init__(f"Field '{field}' cannot be deleted")


class CannotDeleteMandatoryField(DeletionErrorBase):
    ...


class NothingToDelete(DeletionErrorBase):
    ...


def _as_questionnaire_response_answer(item):
    """Questionnaire response answers must be in list form, even if they are a single item"""
    if isinstance(item, (set, list)):
        return list(item)
    return [item]


def new_questionnaire_response_from_template(
    questionnaire_response: QuestionnaireResponse, field_to_update: str, value
) -> QuestionnaireResponse:
    answer = _as_questionnaire_response_answer(value)
    update_in_list_of_dict(
        obj=questionnaire_response.responses, key=field_to_update, value=answer
    )
    non_empty_responses = list(filter(bool, questionnaire_response.responses))
    return questionnaire_response.questionnaire.respond(non_empty_responses)


def update_device_metadata(
    device: Device,
    model: type[NhsAccreditedSystem] | type[NhsMhs],
    modification_type: ModificationType,
    field_alias: str,
    new_values: list,
) -> Device:
    field_name = model.get_field_name_for_alias(alias=field_alias)
    ((questionnaire_response,),) = device.questionnaire_responses.values()
    _current_values = questionnaire_response.get_response(question_name=field_name)

    if modification_type == ModificationType.ADD:
        _updated_unique_values = list(set(*_current_values, *new_values))
        parsed_values = model.parse_and_validate_field(
            model=model, field=field_name, value=_updated_unique_values
        )
    elif modification_type == ModificationType.REPLACE:
        parsed_values = model.parse_and_validate_field(
            model=model, field=field_name, value=new_values
        )
    elif modification_type == ModificationType.DELETE:
        if model.is_mandatory_field(field_name):
            raise CannotDeleteMandatoryField(field_name)
        if not _current_values:
            raise NothingToDelete(field_name)
        parsed_values = []

    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field_name,
        value=parsed_values,
    )
    device.update_questionnaire_response(
        questionnaire_response_index=0,
        questionnaire_response=new_questionnaire_response,
    )
    return device
