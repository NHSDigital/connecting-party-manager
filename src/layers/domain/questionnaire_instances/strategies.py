from domain.core.error import ConfigurationError
from domain.questionnaire_instances.constants import QuestionnaireInstance
from sds.epr.constants import SdsFieldName


def check_missing_fields(
    required_fields: set[str], provided_fields: set[str], questionnaire_name: str
):
    missing_fields = required_fields - provided_fields
    if missing_fields:
        raise ConfigurationError(
            f"The following required fields are missing in the response to {questionnaire_name}: {', '.join(missing_fields)}"
        )


def generate_spine_mhs_fields(
    response: dict, ods_code: str, party_key: str, today: str
) -> None:
    check_missing_fields(
        required_fields={SdsFieldName.MHS_FQDN},
        provided_fields=response.keys(),
        questionnaire_name=QuestionnaireInstance.SPINE_MHS,
    )
    fqdn = response.get(SdsFieldName.MHS_FQDN)

    response[str(SdsFieldName.ADDRESS)] = f"https://{fqdn}"
    response[str(SdsFieldName.PARTY_KEY)] = party_key
    response[str(SdsFieldName.MANAGING_ORGANIZATION)] = ods_code
    response[str(SdsFieldName.DATE_APPROVED)] = today
    response[str(SdsFieldName.DATE_REQUESTED)] = today
    response[str(SdsFieldName.DATE_DNS_APPROVED)] = None


def generate_spine_mhs_message_sets_fields(response: dict, party_key: str):
    check_missing_fields(
        required_fields={SdsFieldName.MHS_SN, SdsFieldName.MHS_IN},
        provided_fields=response.keys(),
        questionnaire_name=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS,
    )
    mhs_sn = response[SdsFieldName.MHS_SN]
    mhs_in = response[SdsFieldName.MHS_IN]

    interaction_id = f"{mhs_sn}:{mhs_in}"
    cpa_id = f"{party_key}:{interaction_id}"

    response[str(SdsFieldName.INTERACTION_ID)] = interaction_id
    response[str(SdsFieldName.CPA_ID)] = cpa_id
    response[str(SdsFieldName.UNIQUE_IDENTIFIER)] = cpa_id


def generate_spine_as_fields(
    response: dict,
    ods_code: str,
    party_key: str,
    product_id: str,
    asid: str,
    today: str,
) -> None:
    check_missing_fields(
        required_fields={SdsFieldName.ODS_CODE},
        provided_fields=response.keys(),
        questionnaire_name=QuestionnaireInstance.SPINE_AS,
    )
    nhs_id_code = response[str(SdsFieldName.ODS_CODE)]

    response[str(SdsFieldName.MANUFACTURING_ORG)] = ods_code
    response[str(SdsFieldName.PARTY_KEY)] = party_key
    response[str(SdsFieldName.PRODUCT_KEY)] = product_id
    response[str(SdsFieldName.ASID)] = asid
    response[str(SdsFieldName.DATE_APPROVED)] = today
    response[str(SdsFieldName.DATE_REQUESTED)] = today
    response[str(SdsFieldName.CLIENT_ODS_CODES)] = [nhs_id_code]
    response[str(SdsFieldName.TEMP_UID)] = None
