import json

import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device_reference_data.v1 import QuestionnaireResponseUpdatedEvent
from domain.core.questionnaire.tests.test_questionnaire_v3 import VALID_SCHEMA
from domain.core.questionnaire.v3 import Questionnaire

from test_helpers.uuid import consistent_uuid


@pytest.fixture
def questionnaire() -> Questionnaire:
    return Questionnaire(
        name="my-questionnaire", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )


def test_add_questionnaire_response(questionnaire: Questionnaire):
    product = CpmProduct(
        name="my-product", ods_code="AAA", product_team_id=consistent_uuid(1)
    )

    questionnaire_response = questionnaire.validate({"size": 4, "colour": "white"})
    device_reference_data = product.create_device_reference_data(
        name="my-device-reference-data"
    )
    event = device_reference_data.add_questionnaire_response(
        questionnaire_response=questionnaire_response
    )
    assert isinstance(event, QuestionnaireResponseUpdatedEvent)
