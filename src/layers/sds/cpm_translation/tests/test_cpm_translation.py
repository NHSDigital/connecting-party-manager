from datetime import datetime
from itertools import chain
from string import ascii_letters, digits
from typing import Generator

import pytest
from domain.core.device.v2 import DeviceDeletedEvent, DeviceType, Status
from domain.core.questionnaire.v2 import Questionnaire
from domain.core.root.v2 import Root
from domain.core.validation import ODS_CODE_REGEX, SdsId
from domain.repository.device_repository.v2 import DeviceRepository
from etl_utils.ldif.model import DistinguishedName
from event.aws.client import dynamodb_client
from event.json import json_load
from hypothesis import given, settings
from hypothesis.provisional import urls
from hypothesis.strategies import builds, from_regex, just, sets, text
from sds.cpm_translation.translations import (
    delete_devices,
    nhs_accredited_system_to_cpm_devices,
    nhs_mhs_to_cpm_device,
    translate,
)
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.sds_deletion_request import SdsDeletionRequest

from etl.sds.tests.constants import EtlTestDataPath
from etl.sds.worker.transform_update.utils import export_events
from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my_table"

DUMMY_DISTINGUISHED_NAME = DistinguishedName(
    parts=(("ou", "services"), ("uniqueidentifier", "foobar"), ("o", "nhs"))
)
EXPECTED_EVENTS_MHS = [
    "device_created_event",
    "device_key_added_event",
    "questionnaire_response_updated_event",
    "device_tags_added_event",
]
EXPECTED_EVENTS_ACCREDITED_SYSTEM = [
    "device_created_event",
    "device_key_added_event",
    "questionnaire_response_updated_event",
    "device_tags_added_event",
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
    nhsasclient=sets(from_regex(ODS_CODE_REGEX, fullmatch=True), min_size=1),
    nhsassvcia=sets(text(alphabet="abc", min_size=1, max_size=1), min_size=1),
    uniqueidentifier=text(alphabet=digits, min_size=1, max_size=8),
)


@pytest.fixture
def repository(
    request: pytest.FixtureRequest,
) -> Generator[DeviceRepository, None, None]:
    if request.node.get_closest_marker("integration"):
        table_name = read_terraform_output("dynamodb_table_name.value")
        client = dynamodb_client()
        yield DeviceRepository(table_name=table_name, dynamodb_client=client)
    else:
        with mock_table(TABLE_NAME) as client:
            yield DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)


@settings(deadline=1500)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_nhs_mhs_to_cpm_device(nhs_mhs: NhsMhs):
    device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    events = device.export_events()
    event_names = list(chain.from_iterable(map(dict.keys, events)))
    assert event_names == EXPECTED_EVENTS_MHS


@settings(deadline=1500)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_nhs_mhs_to_cpm_device_updates(nhs_mhs: NhsMhs):
    device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    events = device.export_events()
    event_names = list(chain.from_iterable(map(dict.keys, events)))
    assert event_names[: len(EXPECTED_EVENTS_MHS)] == EXPECTED_EVENTS_MHS
    assert event_names[-1] == "device_tags_added_event"


@settings(deadline=500)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_nhs_accredited_system_to_cpm_devices(
    nhs_accredited_system: NhsAccreditedSystem,
):
    for i, device in enumerate(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        ),
        start=1,
    ):
        events = device.export_events()
        event_names = list(chain.from_iterable(map(dict.keys, events)))
        assert event_names == EXPECTED_EVENTS_ACCREDITED_SYSTEM
    assert i > 0


@settings(deadline=1000, max_examples=50)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_nhs_accredited_system_to_cpm_devices_updates(
    nhs_accredited_system: NhsAccreditedSystem,
):
    for i, device in enumerate(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        ),
        start=1,
    ):
        events = device.export_events()
        event_names = list(chain.from_iterable(map(dict.keys, events)))
        assert (
            event_names[: len(EXPECTED_EVENTS_ACCREDITED_SYSTEM)]
            == EXPECTED_EVENTS_ACCREDITED_SYSTEM
        )
        assert event_names[-1] == "device_tags_added_event"

    assert i > 0


@pytest.mark.s3(EtlTestDataPath.FULL_JSON)
def test_translate(test_data_paths):
    (path,) = test_data_paths
    with open(path) as f:
        data = json_load(f)
    assert len(data) > 0

    for obj, _devices in zip(
        data,
        map(lambda record: translate(obj=record, repository=None, bulk=False), data),
    ):
        events = export_events(_devices)
        event_names = list(chain.from_iterable(map(dict.keys, events)))
        ods_codes = obj.get("nhs_as_client") or ["dummy_org"]
        n_ods_codes = len(ods_codes)
        assert event_names == EXPECTED_EVENTS_MHS * n_ods_codes, obj


@pytest.mark.integration
def test_delete_devices(repository: DeviceRepository):
    # Set initial state
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    _questionnaire = Questionnaire(name="my_questionnaire", version=1)
    _questionnaire.add_question(
        name="unique_identifier", answer_types=(str,), mandatory=True
    )
    _questionnaire_response = _questionnaire.respond(
        responses=[{"unique_identifier": ["001"]}]
    )
    _device_1 = product_team.create_device(
        name="Device-1", device_type=DeviceType.PRODUCT
    )
    _device_1.add_questionnaire_response(questionnaire_response=_questionnaire_response)
    _device_1.add_tag(unique_identifier="001")
    repository.write(_device_1)

    _device_2 = product_team.create_device(
        name="Device-2", device_type=DeviceType.PRODUCT
    )
    _device_2.add_questionnaire_response(questionnaire_response=_questionnaire_response)
    _device_2.add_tag(unique_identifier="001")
    repository.write(_device_2)

    deletion_request = SdsDeletionRequest(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "001"), ("o", "nhs"))
        ),
        object_class="delete",
        unique_identifier="001",
    )

    devices = delete_devices(deletion_request=deletion_request, repository=repository)
    (event_1, event_2) = sorted(
        chain.from_iterable(device.events for device in devices),
        key=lambda event: event.name,
    )
    assert event_1 == DeviceDeletedEvent(
        id=_device_1.id,
        name=_device_1.name,
        device_type=_device_1.device_type,
        product_team_id=_device_1.product_team_id,
        ods_code=_device_1.ods_code,
        status=Status.INACTIVE,
        created_on=_device_1.created_on,
        updated_on=event_1.updated_on,
        deleted_on=event_1.deleted_on,
        keys=_device_1.keys,
        tags=set(),
        questionnaire_responses=_device_1.questionnaire_responses,
        deleted_tags={t.dict() for t in _device_1.tags},
    )
    assert isinstance(event_1.updated_on, datetime)
    assert isinstance(event_1.deleted_on, datetime)
    assert event_1.deleted_on == event_1.updated_on

    assert event_2 == DeviceDeletedEvent(
        id=_device_2.id,
        name=_device_2.name,
        device_type=_device_1.device_type,
        product_team_id=_device_2.product_team_id,
        ods_code=_device_2.ods_code,
        status=Status.INACTIVE,
        created_on=_device_2.created_on,
        updated_on=event_2.updated_on,
        deleted_on=event_2.deleted_on,
        keys=_device_2.keys,
        tags=set(),
        questionnaire_responses=_device_2.questionnaire_responses,
        deleted_tags={t.dict() for t in _device_2.tags},
    )
    assert isinstance(event_2.updated_on, datetime)
    assert isinstance(event_2.deleted_on, datetime)
    assert event_2.deleted_on == event_2.updated_on


@pytest.mark.integration
def test_delete_devices_no_questionnaire(repository: DeviceRepository):
    deletion_request = SdsDeletionRequest(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "001"), ("o", "nhs"))
        ),
        object_class="delete",
        unique_identifier="001",
    )

    devices = delete_devices(deletion_request=deletion_request, repository=repository)
    assert len(devices) == 0


@pytest.mark.integration
def test_delete_devices_no_matching_device(repository: DeviceRepository):
    # Set initial state
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(
        id="6f8c285e-04a2-4194-a84e-dabeba474ff7", name="Team"
    )
    _questionnaire = Questionnaire(name="my_questionnaire", version=1)
    _questionnaire.add_question(
        name="unique_identifier", answer_types=(str,), mandatory=True
    )
    _questionnaire_response = _questionnaire.respond(
        responses=[{"unique_identifier": ["001"]}]
    )
    _device = product_team.create_device(
        name="Device-1", device_type=DeviceType.PRODUCT
    )
    _device.add_questionnaire_response(questionnaire_response=_questionnaire_response)
    _device.add_tag(unique_identifier="001")
    repository.write(_device)

    deletion_request = SdsDeletionRequest(
        _distinguished_name=DistinguishedName(
            parts=(
                ("ou", "services"),
                ("uniqueidentifier", "does not exist"),
                ("o", "nhs"),
            )
        ),
        object_class="delete",
        unique_identifier="does not exist",
    )

    devices = delete_devices(deletion_request=deletion_request, repository=repository)
    assert len(devices) == 0
