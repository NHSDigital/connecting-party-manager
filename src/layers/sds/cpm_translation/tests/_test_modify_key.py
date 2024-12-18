from dataclasses import astuple

import pytest
from domain.core.device import Device, DeviceTag, Status
from hypothesis import given, settings
from sds.cpm_translation.modify_key import (
    InvalidModificationRequest,
    NotAnSdsKey,
    _get_msg_handling_system_key,
    copy_new_accredited_system_from_sibling_device,
    get_modify_key_function,
    replace_accredited_systems,
    replace_msg_handling_system,
)
from sds.cpm_translation.tests._test_cpm_translation import (
    NHS_ACCREDITED_SYSTEM_STRATEGY,
    NHS_MHS_STRATEGY,
)
from sds.cpm_translation.translations import (
    nhs_accredited_system_to_cpm_devices,
    nhs_mhs_to_cpm_device,
)
from sds.cpm_translation.utils import get_in_list_of_dict
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import MessageHandlingSystemKey, NhsMhs


@pytest.mark.parametrize(
    ("model", "modification_type", "field", "result"),
    [
        (
            NhsAccreditedSystem,
            ModificationType.ADD,
            "nhs_as_client",
            copy_new_accredited_system_from_sibling_device,
        ),
        (
            NhsAccreditedSystem,
            ModificationType.REPLACE,
            "nhs_as_client",
            replace_accredited_systems,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_mhs_party_key",
            replace_msg_handling_system,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_mhs_svc_ia",
            replace_msg_handling_system,
        ),
        (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_id_code",
            replace_msg_handling_system,
        ),
    ],
)
def test_get_modify_key_function(model, modification_type, field, result):
    assert (
        get_modify_key_function(
            model=model, modification_type=modification_type, field_name=field
        )
        is result
    )


@pytest.mark.parametrize(
    ("model", "modification_type", "field"),
    [
        (NhsAccreditedSystem, ModificationType.DELETE, "nhs_as_client"),
        (NhsMhs, ModificationType.ADD, "nhs_mhs_party_key"),
        (NhsMhs, ModificationType.ADD, "nhs_mhs_svc_ia"),
        (NhsMhs, ModificationType.ADD, "nhs_id_code"),
        (NhsMhs, ModificationType.DELETE, "nhs_mhs_party_key"),
        (NhsMhs, ModificationType.DELETE, "nhs_mhs_svc_ia"),
        (NhsMhs, ModificationType.DELETE, "nhs_id_code"),
    ],
)
def test_get_modify_key_function_invalid(model, modification_type, field):
    with pytest.raises(InvalidModificationRequest):
        get_modify_key_function(
            model=model, modification_type=modification_type, field_name=field
        )


@pytest.mark.parametrize("model", (NhsAccreditedSystem, NhsMhs))
@pytest.mark.parametrize(
    "modification_type",
    (ModificationType.ADD, ModificationType.REPLACE, ModificationType.DELETE),
)
def test_get_modify_key_function_other(model, modification_type):
    with pytest.raises(NotAnSdsKey):
        get_modify_key_function(
            model=model, modification_type=modification_type, field_name="foo"
        )


def _test_device_updated(
    old_device: Device,
    new_device: Device,
    original_tags: list[DeviceTag],
    expected_ods_code,
):
    assert new_device.product_team_id == old_device.product_team_id
    assert new_device.ods_code == expected_ods_code
    assert new_device.name == old_device.name

    (old_key,) = old_device.keys
    (new_key,) = new_device.keys

    expected_new_key_name = f"{expected_ods_code}:{new_key.key_value.split(':')[1]}"
    assert new_key.key_type is old_key.key_type
    assert new_key.key_value == expected_new_key_name

    (questionnaire_response_by_datetime,) = new_device.questionnaire_responses.values()
    (questionnaire_response,) = questionnaire_response_by_datetime.values()

    assert get_in_list_of_dict(questionnaire_response.answers, key="nhs_as_client") == [
        expected_ods_code
    ]

    expected_tags = [
        DeviceTag(
            **{
                field_name: (
                    expected_ods_code if field_name == "nhs_as_client" else value
                )
                for (field_name, value) in tag.components
            }
        )
        for tag in original_tags
    ]
    assert set(expected_tags) == set(new_device.tags)

    return True


def _test_devices_updated(
    old_device: Device,
    new_devices: list[Device],
    expected_ods_codes: list[str],
    original_tags: list[DeviceTag],
):
    for ods_code, new_device in zip(
        expected_ods_codes,
        sorted(new_devices, key=lambda d: expected_ods_codes.index(d.ods_code)),
    ):
        return _test_device_updated(
            old_device=old_device,
            new_device=new_device,
            expected_ods_code=ods_code,
            original_tags=original_tags,
        )
    return True


def _test_deleted_devices(
    devices: list[Device],
    old_devices: list[Device],
    modified_devices: list[Device],
    original_tags: list[DeviceTag],
    n_expected_new_devices,
    expected_ods_codes,
):
    assert all(d.status is Status.INACTIVE for d in old_devices)

    # Test that new devices are active
    new_devices = modified_devices[-n_expected_new_devices:]
    assert len(new_devices) == n_expected_new_devices
    assert all(d.status is Status.ACTIVE for d in new_devices)

    assert _test_devices_updated(
        old_device=devices[0],
        new_devices=new_devices,
        expected_ods_codes=expected_ods_codes,
        original_tags=original_tags,
    )


@settings(deadline=3000)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_new_accredited_system(nhs_accredited_system):
    devices = list(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        )
    )
    original_tags = devices[0].tags

    updated_devices = list(
        copy_new_accredited_system_from_sibling_device(
            devices=devices, field_name="nhs_as_client", value=["foo"]
        )
    )
    assert devices == updated_devices[:-1]  # the first n devices are identical
    old_device = devices[0]
    new_device = updated_devices[-1]

    _test_device_updated(
        old_device=old_device,
        new_device=new_device,
        expected_ods_code="foo",
        original_tags=original_tags,
    )


@settings(deadline=3000)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_replace_accredited_systems_no_deletes(nhs_accredited_system):
    # Set up initial state
    devices = list(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        )
    )
    original_tags = devices[0].tags

    old_ods_codes = [device.ods_code for device in devices]
    new_ods_codes = ["foo", "bar"]
    n_expected_new_devices = len(new_ods_codes)

    modified_devices = list(
        replace_accredited_systems(
            devices=devices,
            field_name="nhs_as_client",
            value=old_ods_codes + new_ods_codes,
        )
    )
    # Test that nothing was deleted
    assert all(d.status is Status.ACTIVE for d in modified_devices)

    old_devices = modified_devices[:-n_expected_new_devices]
    assert old_devices == devices

    new_devices = modified_devices[-n_expected_new_devices:]
    assert len(new_devices) == n_expected_new_devices

    old_device = devices[0]
    assert _test_devices_updated(
        old_device=old_device,
        new_devices=new_devices,
        expected_ods_codes=new_ods_codes,
        original_tags=original_tags,
    )


@settings(deadline=3000)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_replace_accredited_systems_with_old_devices_deleted(nhs_accredited_system):
    devices = list(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        )
    )
    original_tags = devices[0].tags

    new_ods_codes = ["foo", "bar"]
    n_expected_new_devices = len(new_ods_codes)

    modified_devices = list(
        replace_accredited_systems(
            devices=devices, field_name="nhs_as_client", value=new_ods_codes
        )
    )
    # Test that old devices are inactive
    old_devices = modified_devices[:-n_expected_new_devices]
    _test_deleted_devices(
        devices=devices,
        old_devices=old_devices,
        modified_devices=modified_devices,
        n_expected_new_devices=n_expected_new_devices,
        expected_ods_codes=new_ods_codes,
        original_tags=original_tags,
    )


@settings(deadline=3000)
@given(nhs_accredited_system=NHS_ACCREDITED_SYSTEM_STRATEGY)
def test_replace_accredited_systems_with_some_devices_deleted(nhs_accredited_system):
    devices = list(
        nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system, bulk=False
        )
    )
    original_tags = devices[0].tags

    new_ods_codes = ["foo", "bar"]
    old_ods_codes = [devices[0].ods_code]  # i.e. keep the first old device active
    n_expected_new_devices = len(new_ods_codes)

    modified_devices = list(
        replace_accredited_systems(
            devices=devices,
            field_name="nhs_as_client",
            value=old_ods_codes + new_ods_codes,
        )
    )

    # Test that first old device is still active
    first_old_device = modified_devices[0]
    assert first_old_device == devices[0]
    assert first_old_device.status is Status.ACTIVE

    # Test that all old devices other than the first are inactive
    old_devices = modified_devices[1:-n_expected_new_devices]
    assert [first_old_device] + old_devices == devices
    _test_deleted_devices(
        devices=devices,
        old_devices=old_devices,
        modified_devices=modified_devices,
        n_expected_new_devices=n_expected_new_devices,
        expected_ods_codes=new_ods_codes,
        original_tags=original_tags,
    )


@settings(deadline=3000)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test__get_msg_handling_system_key(nhs_mhs: NhsMhs):
    device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    (questionnaire_response_by_datetime,) = device.questionnaire_responses.values()
    (created_on_str,) = questionnaire_response_by_datetime.keys()

    mhs_key = _get_msg_handling_system_key(
        responses=device.questionnaire_responses["spine_endpoint/1"][
            created_on_str
        ].answers
    )
    expected_key = MessageHandlingSystemKey(
        nhs_id_code=nhs_mhs.nhs_id_code,
        nhs_mhs_party_key=nhs_mhs.nhs_mhs_party_key,
        nhs_mhs_svc_ia=nhs_mhs.nhs_mhs_svc_ia,
    )

    assert mhs_key == expected_key
    assert astuple(mhs_key) == (
        nhs_mhs.nhs_id_code,
        nhs_mhs.nhs_mhs_party_key,
        nhs_mhs.nhs_mhs_svc_ia,
    )


def _test_mhs_devices(
    new_device: Device,
    deleted_device: Device,
    old_device: Device,
    expected_ods_code: str,
    original_tags: list[DeviceTag],
    **updated_fields,
):
    assert deleted_device is old_device
    assert deleted_device.status is Status.INACTIVE
    assert new_device.product_team_id == old_device.product_team_id
    assert new_device.ods_code == expected_ods_code
    assert new_device.name == old_device.name

    expected_tags = {
        DeviceTag(
            **{
                field_name: (
                    updated_fields[field_name]
                    if field_name in updated_fields
                    else value
                )
                for (field_name, value) in tag.components
            }
        )
        for tag in original_tags
    }
    assert expected_tags == new_device.tags

    return True


@settings(deadline=3000)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_replace_msg_handling_system_nhs_id_code(nhs_mhs: NhsMhs):
    old_device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    original_tags = old_device.tags

    deleted_device, new_device = replace_msg_handling_system(
        devices=[old_device], field_name="nhs_id_code", value="foo"
    )
    assert _test_mhs_devices(
        new_device=new_device,
        deleted_device=deleted_device,
        old_device=old_device,
        expected_ods_code="foo",
        original_tags=original_tags,
        nhs_id_code="foo",
    )

    (device_key,) = old_device.keys
    (new_device_key,) = new_device.keys

    (questionnaire_response_by_datetime,) = old_device.questionnaire_responses.values()
    (created_on_str,) = questionnaire_response_by_datetime.keys()

    old_mhs_key = _get_msg_handling_system_key(
        responses=old_device.questionnaire_responses["spine_endpoint/1"][
            created_on_str
        ].answers
    )

    expected_new_key_name = ":".join(
        ("foo", old_mhs_key.nhs_mhs_party_key, old_mhs_key.nhs_mhs_svc_ia)
    )
    assert expected_new_key_name == new_device_key.key_value
    assert new_device_key.key_type is device_key.key_type
    assert new_device_key.key_value == expected_new_key_name


@settings(deadline=3000)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_replace_msg_handling_system_nhs_mhs_party_key(nhs_mhs: NhsMhs):
    old_device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    original_tags = old_device.tags

    deleted_device, new_device = replace_msg_handling_system(
        devices=[old_device], field_name="nhs_mhs_party_key", value="foo-0"
    )
    assert _test_mhs_devices(
        new_device=new_device,
        deleted_device=deleted_device,
        old_device=old_device,
        expected_ods_code=old_device.ods_code,
        original_tags=original_tags,
        nhs_mhs_party_key="foo-0",
    )

    (device_key,) = old_device.keys
    (new_device_key,) = new_device.keys

    (questionnaire_response_by_datetime,) = old_device.questionnaire_responses.values()
    (created_on_str,) = questionnaire_response_by_datetime.keys()

    old_mhs_key = _get_msg_handling_system_key(
        responses=old_device.questionnaire_responses["spine_endpoint/1"][
            created_on_str
        ].answers
    )

    expected_new_key_name = ":".join(
        (old_mhs_key.nhs_id_code, "foo-0", old_mhs_key.nhs_mhs_svc_ia)
    )
    assert new_device_key.key_type is device_key.key_type
    assert new_device_key.key_value == expected_new_key_name


@settings(deadline=3000)
@given(nhs_mhs=NHS_MHS_STRATEGY)
def test_replace_msg_handling_system_nhs_mhs_svc_ia(nhs_mhs: NhsMhs):
    old_device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=False)
    original_tags = old_device.tags

    deleted_device, new_device = replace_msg_handling_system(
        devices=[old_device], field_name="nhs_mhs_svc_ia", value="foo"
    )
    assert _test_mhs_devices(
        new_device=new_device,
        deleted_device=deleted_device,
        old_device=old_device,
        expected_ods_code=old_device.ods_code,
        original_tags=original_tags,
        nhs_mhs_svc_ia="foo",
    )

    (device_key,) = old_device.keys
    (new_device_key,) = new_device.keys

    (questionnaire_response_by_datetime,) = old_device.questionnaire_responses.values()
    (created_on_str,) = questionnaire_response_by_datetime.keys()

    old_mhs_key = _get_msg_handling_system_key(
        responses=old_device.questionnaire_responses["spine_endpoint/1"][
            created_on_str
        ].answers
    )

    expected_new_key_name = ":".join(
        (old_mhs_key.nhs_id_code, old_mhs_key.nhs_mhs_party_key, "foo")
    )
    assert new_device_key.key_type is device_key.key_type
    assert new_device_key.key_value == expected_new_key_name
