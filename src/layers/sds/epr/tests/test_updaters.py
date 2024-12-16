import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.epr.constants import SdsFieldName
from sds.epr.creators import (
    create_additional_interactions,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
)
from sds.epr.updaters import (
    remove_erroneous_additional_interactions,
    update_message_sets,
)
from sds.epr.utils import get_interaction_ids

from test_helpers.dynamodb import mock_table


@pytest.fixture
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture
def product(product_team):
    return create_epr_product(
        product_team=product_team, product_name="foo", party_key="AAA-111111"
    )


@pytest.fixture
def message_sets(product: CpmProduct):
    questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_data = [
        questionnaire.validate(
            {
                str(SdsFieldName.INTERACTION_ID): interaction_id,
                "MHS SN": "",
                "MHS IN": "",
            }
        )
        for interaction_id in ("foo", "baz", "bob")
    ]

    return create_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        message_set_data=message_set_data,
    )


@pytest.fixture
def additional_interactions(product: CpmProduct):
    questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    additional_interactions_data = [
        questionnaire.validate({str(SdsFieldName.INTERACTION_ID): interaction_id})
        for interaction_id in ("foo", "bar", "baz", "beep")
    ]
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=additional_interactions_data,
    )


@pytest.fixture
def device_repository():
    with mock_table("foo") as client:
        yield DeviceRepository(table_name="foo", dynamodb_client=client)


def test_remove_erroneous_additional_interactions(
    message_sets: DeviceReferenceData, additional_interactions: DeviceReferenceData
):
    initial_interaction_ids = get_interaction_ids(additional_interactions)
    assert initial_interaction_ids == {"foo", "bar", "baz", "beep"}

    _additional_interactions = remove_erroneous_additional_interactions(
        message_sets=message_sets, additional_interactions=additional_interactions
    )

    final_interaction_ids = get_interaction_ids(_additional_interactions)
    assert final_interaction_ids == {"bar", "beep"}


def test_update_message_sets(message_sets: DeviceReferenceData):
    initial_state = message_sets.state()

    questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_data = [
        questionnaire.validate(
            {
                str(SdsFieldName.INTERACTION_ID): interaction_id,
                "MHS SN": "the new value",
                "MHS IN": "the new value",
            }
        )
        for interaction_id in ("foo", "bar")
    ]
    _message_sets = update_message_sets(
        message_sets=message_sets, message_set_data=message_set_data
    )
    final_state = _message_sets.state()

    qid = f"{QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}/1"
    assert final_state.pop("updated_on") > initial_state.pop("updated_on")
    questionnaire_responses = final_state.pop("questionnaire_responses")[qid]
    assert len(questionnaire_responses) == 4

    qr_data = [qr["data"] for qr in questionnaire_responses]
    assert qr_data == [
        {
            "Interaction ID": "baz",
            "MHS IN": "",
            "MHS SN": "",
        },
        {
            "Interaction ID": "bob",
            "MHS IN": "",
            "MHS SN": "",
        },
        {
            "Interaction ID": "foo",  # replaced old "foo"
            "MHS IN": "the new value",
            "MHS SN": "the new value",
        },
        {
            "Interaction ID": "bar",
            "MHS IN": "the new value",
            "MHS SN": "the new value",
        },
    ]

    del initial_state["questionnaire_responses"]
    assert initial_state == final_state
