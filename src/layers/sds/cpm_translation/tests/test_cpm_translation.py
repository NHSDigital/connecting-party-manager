from itertools import chain
from string import ascii_letters, digits

import pytest
from domain.core.load_questionnaire import render_questionnaire
from domain.core.questionnaires import QuestionnaireInstance
from domain.core.validation import ODS_CODE_REGEX, SdsId
from etl_utils.ldif.model import DistinguishedName
from event.json import json_load
from hypothesis import given, settings
from hypothesis.provisional import urls
from hypothesis.strategies import builds, from_regex, just, sets, text
from sds.cpm_translation import (
    nhs_accredited_system_to_cpm_devices,
    nhs_mhs_to_cpm_device,
    translate,
)
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

DUMMY_DISTINGUISHED_NAME = DistinguishedName(
    parts=(("ou", "services"), ("uniqueidentifier", "foobar"), ("o", "nhs"))
)
EXPECTED_EVENTS = [
    "device_created_event",
    "device_key_added_event",
    "questionnaire_instance_event",
    "questionnaire_response_added_event",
]


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
    nhsmhspartykey=from_regex(
        SdsId.MessageHandlingSystem.PARTY_KEY_REGEX, fullmatch=True
    ),
    nhsmhssvcia=text(alphabet=ascii_letters + digits + ":", min_size=1),
    nhsmhsendpoint=urls(),
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
    nhsasclient=sets(from_regex(ODS_CODE_REGEX, fullmatch=True)),
    uniqueidentifier=text(alphabet=digits, min_size=1, max_size=8),
)


@settings(deadline=1000)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_nhs_mhs_to_cpm_device(nhs_mhs: NhsMhs):
    questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT, questionnaire_version=1
    )
    device = nhs_mhs_to_cpm_device(
        nhs_mhs=nhs_mhs,
        questionnaire=questionnaire,
        _questionnaire=questionnaire.dict(),
    )
    events = device.export_events()
    event_names = list(chain.from_iterable(map(dict.keys, events)))
    assert event_names == EXPECTED_EVENTS


@settings(deadline=1000)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_nhs_accredited_system_to_cpm_devices(
    nhs_accredited_system: NhsAccreditedSystem,
):
    questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_DEVICE, questionnaire_version=1
    )
    for i, device in enumerate(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system,
            questionnaire=questionnaire,
            _questionnaire=questionnaire.dict(),
        ),
        start=1,
    ):
        events = device.export_events()
        event_names = list(chain.from_iterable(map(dict.keys, events)))
        assert event_names == EXPECTED_EVENTS
    assert i > 0


@pytest.mark.s3("sds/etl/bulk/1701246-fix-18032023.json")
def test_translate(test_data_paths):
    (path,) = test_data_paths
    with open(path) as f:
        data = json_load(f)
    assert len(data) > 0

    spine_device_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_DEVICE, questionnaire_version=1
    )
    _spine_device_questionnaire = spine_device_questionnaire.dict()
    spine_endpoint_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT, questionnaire_version=1
    )
    _spine_endpoint_questionnaire = spine_endpoint_questionnaire.dict()

    for obj, events in zip(
        data,
        map(
            lambda record: translate(
                obj=record,
                spine_device_questionnaire=spine_device_questionnaire,
                _spine_device_questionnaire=_spine_device_questionnaire,
                spine_endpoint_questionnaire=spine_endpoint_questionnaire,
                _spine_endpoint_questionnaire=_spine_endpoint_questionnaire,
            ),
            data,
        ),
    ):
        event_names = list(chain.from_iterable(map(dict.keys, events)))
        ods_codes = obj.get("nhs_as_client") or ["dummy_org"]
        n_ods_codes = len(ods_codes)
        assert event_names == EXPECTED_EVENTS * n_ods_codes, obj
