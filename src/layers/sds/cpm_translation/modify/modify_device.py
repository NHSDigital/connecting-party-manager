from domain.core.device import Device
from pydantic import ValidationError
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

from .utils import InvalidModificationRequest, new_questionnaire_response_from_template


class MandatoryFieldError(Exception):
    def __init__(self, field):
        super().__init__(f"Field '{field}' cannot be null")


class NoValuesToRemove(Exception):
    pass


def _unique_list(*items):
    return list(set(items))


def _parse_and_validate_field(
    model: type[NhsAccreditedSystem] | type[NhsMhs], field: str, value
) -> list:
    try:
        parsed_value = model.parse_and_validate_field(field=field, value=value)
    except ValidationError:
        raise InvalidModificationRequest(field)

    if isinstance(parsed_value, (set, list)):
        return list(parsed_value)
    else:
        return [parsed_value]


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
        _updated_values = _unique_list(*_current_values, *new_values)
        parsed_values = _parse_and_validate_field(
            model=model, field=field_name, value=_updated_values
        )
    elif modification_type == ModificationType.REPLACE:
        parsed_values = _parse_and_validate_field(
            model=model, field=field_name, value=new_values
        )
    elif modification_type == ModificationType.DELETE:
        if model.is_mandatory_field(field_name):
            raise MandatoryFieldError(field_name)
        if not _current_values:
            raise InvalidModificationRequest(
                field_name, "This device has no such data to delete"
            )
        parsed_values = []

    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field_name,
        new_values=parsed_values,
    )
    device.update_questionnaire_response(
        questionnaire_response_index=0,
        questionnaire_response=new_questionnaire_response,
    )
    return device
