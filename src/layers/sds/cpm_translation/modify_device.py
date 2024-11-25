from domain.core.device import Device
from domain.core.questionnaire import QuestionnaireResponse
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

from .utils import set_device_tags, update_in_list_of_dict


class DeletionErrorBase(Exception):
    def __init__(self, field):
        super().__init__(f"Field '{field}' cannot be deleted")


class CannotDeleteMandatoryField(DeletionErrorBase): ...


class NothingToDelete(DeletionErrorBase): ...


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
        obj=questionnaire_response.answers, key=field_to_update, value=answer
    )
    non_empty_answers = list(filter(bool, questionnaire_response.answers))
    new_questionnaire_response = questionnaire_response.questionnaire.respond(
        non_empty_answers
    )
    new_questionnaire_response.created_on = questionnaire_response.created_on
    return new_questionnaire_response


def update_device_metadata(
    device: Device,
    model: type[NhsAccreditedSystem] | type[NhsMhs],
    modification_type: ModificationType,
    field_alias: str,
    new_values: list,
) -> Device:
    field = model.get_field_name_for_alias(alias=field_alias)
    (questionnaire_response_by_datetime,) = device.questionnaire_responses.values()
    (questionnaire_response,) = questionnaire_response_by_datetime.values()
    questionnaire_response.questionnaire = model.questionnaire()
    _current_values = questionnaire_response.get_response(question_name=field)

    # Replacing with an empty value is another method of deleting
    if modification_type == ModificationType.REPLACE and len(new_values) == 0:
        modification_type = ModificationType.REPLACE_WITH_EMPTY

    if modification_type == ModificationType.ADD:
        _unique_values = {*_current_values, *new_values}
        parsed_values = model.parse_and_validate_field(
            field=field, value=_unique_values
        )
    elif modification_type == ModificationType.REPLACE:
        _unique_values = set(new_values)
        parsed_values = model.parse_and_validate_field(
            field=field, value=_unique_values
        )
    elif modification_type == ModificationType.DELETE:
        if model.is_mandatory_field(field):
            raise CannotDeleteMandatoryField(field)
        if not _current_values:
            raise NothingToDelete(field)
        parsed_values = []
    elif modification_type == ModificationType.REPLACE_WITH_EMPTY:
        if model.is_mandatory_field(field):
            raise CannotDeleteMandatoryField(field)
        parsed_values = []

    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field,
        value=parsed_values,
    )
    device.update_questionnaire_response(
        questionnaire_response=new_questionnaire_response
    )

    device.clear_tags()
    set_device_tags(
        device=device,
        data=new_questionnaire_response.flat_answers,
        model=model.query_params_model(),
    )

    return device
