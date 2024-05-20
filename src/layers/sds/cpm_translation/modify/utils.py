from domain.core.questionnaire import QuestionnaireResponse

from ..utils import update_in_list_of_dict


class InvalidModificationRequest(Exception):
    def __init__(self, field, extra_info=""):
        msg = ". ".join(
            filter(
                bool, (f"Cannot modify field '{field}' with this operation", extra_info)
            )
        )
        super().__init__(msg)


def new_questionnaire_response_from_template(
    questionnaire_response: QuestionnaireResponse, field_to_update: str, new_values
) -> QuestionnaireResponse:
    update_in_list_of_dict(
        obj=questionnaire_response.responses, key=field_to_update, value=new_values
    )
    non_empty_responses = list(filter(bool, questionnaire_response.responses))
    return questionnaire_response.questionnaire.respond(non_empty_responses)
