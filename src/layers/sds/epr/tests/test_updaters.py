import json

import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import (
    Questionnaire,
    QuestionnaireResponseValidationError,
)
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
    UnexpectedModification,
    ldif_add_to_field_in_questionnaire,
    ldif_remove_field_from_questionnaire,
    remove_erroneous_additional_interactions,
    update_message_sets,
)
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
                "MHS CPA ID": f"1234-{interaction_id}",
                "Unique Identifier": f"1234-{interaction_id}",
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
                "MHS CPA ID": f"1234-{interaction_id}",
                "Unique Identifier": f"1234-{interaction_id}",
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
            "MHS CPA ID": "1234-baz",
            "Unique Identifier": "1234-baz",
        },
        {
            "Interaction ID": "bob",
            "MHS IN": "",
            "MHS SN": "",
            "MHS CPA ID": "1234-bob",
            "Unique Identifier": "1234-bob",
        },
        {
            "Interaction ID": "foo",  # replaced old "foo"
            "MHS IN": "the new value",
            "MHS SN": "the new value",
            "MHS CPA ID": "1234-foo",
            "Unique Identifier": "1234-foo",
        },
        {
            "Interaction ID": "bar",
            "MHS IN": "the new value",
            "MHS SN": "the new value",
            "MHS CPA ID": "1234-bar",
            "Unique Identifier": "1234-bar",
        },
    ]

    del initial_state["questionnaire_responses"]
    assert initial_state == final_state


@pytest.fixture
def questionnaire():
    return Questionnaire(
        name="my questionnaire",
        version="1",
        json_schema=json.dumps(
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "sizes": {
                        "type": "array",
                    },
                    "colour": {"type": "string"},
                },
                "additionalProperties": False,
            }
        ),
    )


@pytest.mark.parametrize(
    ["current_data", "field_name_to_modify", "new_values", "updated_data"],
    [
        (
            {"sizes": [5, 7], "colour": "blue"},
            "sizes",
            [6, 8],
            {"sizes": [5, 7, 6, 8], "colour": "blue"},
        ),
        (
            {"colour": "blue"},
            "sizes",
            [6, 8],
            {"sizes": [6, 8], "colour": "blue"},
        ),
        (
            {"sizes": [5, 7]},
            "colour",
            ["red"],
            {"sizes": [5, 7], "colour": "red"},
        ),
    ],
)
def test__ldif_modify_add_to_questionnaire_response(
    current_data, field_name_to_modify, new_values, updated_data, questionnaire
):
    new_questionnaire_response = ldif_add_to_field_in_questionnaire(
        field_name=field_name_to_modify,
        new_values=new_values,
        current_data=current_data,
        questionnaire=questionnaire,
    )
    assert new_questionnaire_response.data == updated_data


@pytest.mark.parametrize(
    ["current_data", "new_colours", "expected_exception"],
    [
        ({"colour": "blue"}, ["red"], UnexpectedModification),
        ({"colour": "blue"}, ["red", "blue"], UnexpectedModification),
        ({}, [1], QuestionnaireResponseValidationError),  # not a string
    ],
)
def test__ldif_modify_add_to_questionnaire_response__errors(
    current_data, new_colours, expected_exception, questionnaire
):
    with pytest.raises(expected_exception):
        ldif_add_to_field_in_questionnaire(
            field_name="colour",
            new_values=new_colours,
            current_data=current_data,
            questionnaire=questionnaire,
        )


def test__ldif_remove_field_from_questionnaire(questionnaire):
    new_questionnaire_response = ldif_remove_field_from_questionnaire(
        field_name="sizes",
        new_values=None,
        current_data={"sizes": [5, 7], "colour": "blue"},
        questionnaire=questionnaire,
    )
    assert new_questionnaire_response.data == {"colour": "blue"}


def test__ldif_remove_field_from_questionnaire__errors(questionnaire: Questionnaire):
    questionnaire.json_schema["required"] = ["sizes"]
    with pytest.raises(UnexpectedModification):
        ldif_remove_field_from_questionnaire(
            field_name="sizes",
            new_values=None,
            current_data={"sizes": [5, 7], "colour": "blue"},
            questionnaire=questionnaire,
        )
