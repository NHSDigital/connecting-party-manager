from string import ascii_letters, digits

from domain.core.validation import ODS_CODE_REGEX, SdsId
from domain.questionnaire_instances.constants import QuestionnaireInstance
from domain.repository.questionnaire_repository import QuestionnaireRepository
from etl_utils.ldif.model import DistinguishedName
from hypothesis import given, settings
from hypothesis.provisional import urls
from hypothesis.strategies import builds, from_regex, just, sets, text
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.tags import is_list_like

DUMMY_DISTINGUISHED_NAME = DistinguishedName(
    parts=(("ou", "services"), ("uniqueidentifier", "foobar"), ("o", "nhs"))
)

NHS_MHS_STRATEGY = builds(
    NhsMhs,
    _distinguished_name=just(DUMMY_DISTINGUISHED_NAME),
    objectclass=just(
        {
            "nhsmhs",
        }
    ),
    nhsidcode=from_regex(ODS_CODE_REGEX, fullmatch=True),
    nhsproductname=text(alphabet=ascii_letters + digits + " -_", min_size=1),
    nhsmhspartykey=from_regex(SdsId.PartyKey.PARTY_KEY_REGEX, fullmatch=True),
    nhsmhssvcia=text(alphabet=ascii_letters + digits + ":", min_size=1),
    nhsmhsendpoint=urls(),
    nhsmhsmanufacturerorg=just("AAA"),
)

NHS_ACCREDITED_SYSTEM_STRATEGY = builds(
    NhsAccreditedSystem,
    _distinguished_name=just(DUMMY_DISTINGUISHED_NAME),
    objectclass=just(
        {
            "nhsas",
        }
    ),
    nhsproductname=text(alphabet=ascii_letters + digits + " -_", min_size=1),
    nhsasclient=sets(from_regex(ODS_CODE_REGEX, fullmatch=True), min_size=1),
    nhsassvcia=sets(text(alphabet="abc", min_size=1, max_size=1), min_size=1),
    uniqueidentifier=text(alphabet=digits, min_size=1, max_size=8),
    nhsmhsmanufacturerorg=just("AAA"),
)


def _apply_field_mapping(name: str, data: dict) -> dict:
    field_mapping = QuestionnaireRepository().read_field_mapping(name)
    questionnaire = QuestionnaireRepository().read(name)

    required_fields = set(questionnaire.json_schema["required"])
    return {
        field_mapping[k]: (sorted(v) if is_list_like(v) else v)
        for k, v in data.items()
        if (k in field_mapping and v is not None)
        or field_mapping.get(k) in required_fields
    }


@settings(deadline=1500)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_spine_as_questionnaires_pass(nhs_accredited_system: NhsAccreditedSystem):
    as_questionnaire = QuestionnaireRepository().read(QuestionnaireInstance.SPINE_AS)
    as_interactions_questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )
    _as_data = nhs_accredited_system.dict()
    as_data = _apply_field_mapping(name=QuestionnaireInstance.SPINE_AS, data=_as_data)
    as_interactions_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS, data=_as_data
    )

    response = as_questionnaire.validate(as_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_AS
    assert response.questionnaire_version == "1"
    assert response.data == as_data

    # Answer the additional_interactions questionnaire once per Interaction ID
    for interaction_id in as_interactions_data["Interaction ID"]:
        _as_interaction_data = {"Interaction ID": interaction_id}
        response = as_interactions_questionnaire.validate(_as_interaction_data)
        assert (
            response.questionnaire_name
            == QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        assert response.questionnaire_version == "1"
        assert response.data == _as_interaction_data


@settings(deadline=1500)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_spine_mhs_questionnaires_pass(nhs_mhs: NhsMhs):
    mhs_questionnaire = QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS)
    mhs_interactions_questionnaire = QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    )
    _mhs_data = nhs_mhs.dict()
    mhs_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS, data=_mhs_data
    )
    mhs_interactions_data = _apply_field_mapping(
        name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS, data=_mhs_data
    )

    response = mhs_questionnaire.validate(mhs_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_MHS
    assert response.questionnaire_version == "1"
    assert response.data == mhs_data

    response = mhs_interactions_questionnaire.validate(mhs_interactions_data)
    assert response.questionnaire_name == QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    assert response.questionnaire_version == "1"
    assert response.data == mhs_interactions_data
