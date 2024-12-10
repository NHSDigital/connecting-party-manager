from domain.core.error import ConfigurationError
from domain.core.timestamp import now
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
from sds.epr.constants import SdsFieldName


# Move this as part of a QuestionnaireInstance refactor
def generate_spine_mhs_fields(response: dict, **kwargs) -> None:
    from domain.repository.questionnaire_repository.v1.questionnaires import (
        QuestionnaireInstance,
    )

    required_fields = [SdsFieldName.BINDING, SdsFieldName.MHS_FQDN]
    missing_fields = [field for field in required_fields if not response.get(field)]
    if missing_fields:
        # use questionnaire instance for questionnaire name?
        raise ConfigurationError(
            f"The following required fields are missing in the response to {QuestionnaireInstance.SPINE_MHS}: {', '.join(missing_fields)}"
        )

    response[str(SdsFieldName.ADDRESS)] = (
        f"{response.get(SdsFieldName.BINDING)}{response.get(SdsFieldName.MHS_FQDN)}"
    )
    party_key = kwargs.get("party_key")
    response[str(SdsFieldName.PARTY_KEY)] = party_key
    response[str(SdsFieldName.MANAGING_ORGANIZATION)] = party_key.split("-")[0]
    response[str(SdsFieldName.DATE_APPROVED)] = str(now())
    response[str(SdsFieldName.DATE_REQUESTED)] = str(now())
    response[str(SdsFieldName.DATE_DNS_APPROVED)] = str(None)


def generate_spine_mhs_message_sets_fields(response: dict, **kwargs):
    """
    Generates system fields for a given questionnaire response.
    """

    # Ensure required fields for system-generated fields are present
    required_fields = [SdsFieldName.MHS_SN, SdsFieldName.MHS_IN]
    missing_fields = [field for field in required_fields if not response.get(field)]
    if missing_fields:
        raise ConfigurationError(
            f"The following required fields are missing in the response to {QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}: {', '.join(missing_fields)}"
        )

    # Generate system fields
    response[str(SdsFieldName.INTERACTION_ID)] = (
        f"{response.get(SdsFieldName.MHS_SN)}:{response.get(SdsFieldName.MHS_IN)}"
    )
    party_key = kwargs.get("party_key")
    response[str(SdsFieldName.CPA_ID)] = (
        f"{party_key}:{response[SdsFieldName.INTERACTION_ID]}"
    )
    response[str(SdsFieldName.UNIQUE_IDENTIFIER)] = response[SdsFieldName.CPA_ID]


# Mapping of QuestionnaireInstance to field generation functions
FIELD_GENERATION_STRATEGIES = {
    "SPINE_MHS": generate_spine_mhs_fields,
    "SPINE_MHS_MESSAGE_SETS": generate_spine_mhs_message_sets_fields,
}
