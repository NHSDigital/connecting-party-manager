import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.repository.questionnaire_repository.v1.questionnaire_repository import (
    QuestionnaireRepository,
)
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.epr.creators import (
    create_additional_interactions,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
)
from sds.epr.getters import get_additional_interactions_data, get_message_set_data
from sds.epr.utils import get_interaction_ids


@pytest.fixture
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture
def product(product_team):
    return create_epr_product(
        product_team=product_team, product_name="foo", party_key="AAA-111111"
    )


@pytest.fixture
def additional_interactions(product: CpmProduct):
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=[],
    )


def test_get_interaction_ids_from_additional_interactions(product: CpmProduct):
    interaction_ids = {"foo", "bar"}
    accredited_systems = [
        {"nhs_as_svc_ia": [interaction_id]} for interaction_id in interaction_ids
    ]

    additional_interactions_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    additional_interactions_data = get_additional_interactions_data(
        accredited_systems=accredited_systems,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )
    additional_interactions = create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=additional_interactions_data,
    )
    assert get_interaction_ids(additional_interactions) == interaction_ids


def test_get_interaction_ids_from_message_sets(product: CpmProduct):
    interaction_ids = {"foo", "bar"}
    message_handling_systems = [
        {"nhs_mhs_svc_ia": interaction_id, "nhs_mhs_in": "", "nhs_mhs_sn": ""}
        for interaction_id in interaction_ids
    ]
    message_set_questionnaire = QuestionnaireRepository().read(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_field_mapping = QuestionnaireRepository().read_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    message_set_data = get_message_set_data(
        message_handling_systems=message_handling_systems,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
    )
    message_sets = create_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        message_set_data=message_set_data,
    )
    assert get_interaction_ids(message_sets) == interaction_ids
