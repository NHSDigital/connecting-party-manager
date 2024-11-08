from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.questionnaire.v3 import Questionnaire
from domain.repository.questionnaire_repository.v2 import QuestionnaireRepository
from domain.request_models.v1 import QuestionnairePathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> QuestionnairePathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return QuestionnairePathParams(**event.path_parameters)


def read_questionnaire(data, cache) -> Questionnaire:
    path_params: QuestionnairePathParams = data[parse_path_params]
    repo = QuestionnaireRepository()
    return repo.read(name=path_params.questionnaire_id)


def questionnaire_to_dict(data, cache) -> tuple[int, dict]:
    questionnaire: Questionnaire = data[read_questionnaire]
    return HTTPStatus.OK, questionnaire.state()


steps = [
    parse_path_params,
    read_questionnaire,
    questionnaire_to_dict,
]
