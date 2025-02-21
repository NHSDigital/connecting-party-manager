import pytest
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team.v1 import ProductTeam
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
from sds.epr.utils import filter_message_set_by_cpa_id, get_interaction_ids


@pytest.fixture
def product_team():
    return create_epr_product_team("AAA")


@pytest.fixture
def product(product_team: ProductTeam):
    return create_epr_product(
        product_team=product_team, product_name="foo", party_key="AAA-111111"
    )


@pytest.fixture
def additional_interactions(product: EprProduct):
    return create_additional_interactions(
        product=product,
        party_key=product.keys[0].key_value,
        additional_interactions_data=[],
    )


def message_sets_factory(product: EprProduct, interaction_ids: set[str]):
    message_handling_systems = [
        {
            "nhs_mhs_svc_ia": interaction_id,
            "nhs_mhs_in": "",
            "nhs_mhs_sn": "",
            "nhs_mhs_cpa_id": f"123-{interaction_id}",
            "unique_identifier": f"123-{interaction_id}",
        }
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
    return create_message_sets(
        product=product,
        party_key=product.keys[0].key_value,
        message_set_data=message_set_data,
    )


def test_get_interaction_ids_from_additional_interactions(product: EprProduct):
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


def test_get_interaction_ids_from_message_sets(product: EprProduct):
    interaction_ids = {"foo", "bar"}
    message_sets = message_sets_factory(
        product=product, interaction_ids=interaction_ids
    )
    assert get_interaction_ids(message_sets) == interaction_ids


@pytest.mark.parametrize("cpa_id_suffix", ["foo", "bar"])
def test_filter_message_set_by_cpa_id(product: EprProduct, cpa_id_suffix):
    interaction_ids = {"foo", "bar"}
    message_sets = message_sets_factory(
        product=product, interaction_ids=interaction_ids
    )
    message_set_foo = filter_message_set_by_cpa_id(
        message_sets=message_sets, cpa_id=f"123-{cpa_id_suffix}"
    )
    assert message_set_foo.data == {
        "Interaction ID": cpa_id_suffix,
        "MHS IN": "",
        "MHS SN": "",
        "MHS CPA ID": f"123-{cpa_id_suffix}",
        "Unique Identifier": f"123-{cpa_id_suffix}",
    }
