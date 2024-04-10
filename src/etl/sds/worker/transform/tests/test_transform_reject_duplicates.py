from contextlib import nullcontext as do_not_raise
from uuid import UUID

import pytest
from domain.core.device import DeviceType
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam

from etl.sds.worker.transform.reject_duplicates import (
    DuplicateSdsKey,
    _get_duplicate_events,
    reject_duplicate_keys,
)


def _device_events():
    product_team = ProductTeam(id=UUID(int=123), name="name", ods_code="ods-code")

    exported_events = []
    device_1 = product_team.create_device(name="device", type=DeviceType.PRODUCT)
    device_1.add_key(type=DeviceKeyType.PRODUCT_ID, key="P.346-346")
    exported_events += device_1.export_events()

    device_2 = product_team.create_device(name="device", type=DeviceType.PRODUCT)
    device_2.add_key(type=DeviceKeyType.PRODUCT_ID, key="P.ACD-CDE")
    exported_events += device_2.export_events()

    device_3 = product_team.create_device(name="device", type=DeviceType.PRODUCT)
    device_3.add_key(type=DeviceKeyType.PRODUCT_ID, key="P.AAA-XXX")
    exported_events += device_3.export_events()

    return exported_events


def test__get_duplicate_events__with_duplicates():
    exported_events = []
    for _ in range(2):
        exported_events += _device_events()

    duplicates = list(_get_duplicate_events(exported_events=exported_events))
    assert len(duplicates) == 3
    assert all(len(events) == 2 for _, events in duplicates)
    assert set(keys for keys, _ in duplicates) == {
        "P.346-346",
        "P.ACD-CDE",
        "P.AAA-XXX",
    }


def test__get_duplicate_events__without_duplicates():
    exported_events = _device_events()
    duplicates = list(_get_duplicate_events(exported_events=exported_events))
    assert duplicates == []


def test_reject_duplicate_keys__with_duplicates():
    exported_events = []
    for _ in range(2):
        exported_events += _device_events()

    with pytest.raises(DuplicateSdsKey):
        reject_duplicate_keys(exported_events=exported_events)


def test_reject_duplicate_keys__without_duplicates():
    exported_events = _device_events()
    with do_not_raise():
        reject_duplicate_keys(exported_events=exported_events)
