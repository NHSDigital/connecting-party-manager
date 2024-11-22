import time
from copy import deepcopy

import pytest
from attr import asdict
from domain.core.device import Device, DeviceCreatedEvent
from domain.core.device_key import DeviceKeyType
from domain.core.enum import Status
from domain.core.root import Root
from domain.repository.compression import pkl_loads_gzip
from domain.repository.device_repository import (
    DeviceRepository,
    InactiveDeviceRepository,
    compress_device_fields,
)
from domain.repository.errors import AlreadyExistsError, ItemNotFound

DEVICE_KEY = "P.WWW-XXX"


@pytest.fixture
def device() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Product Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-1")
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.fixture
def device_with_tag() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Product Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-1")
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    device.add_tag(
        nhs_as_client="5NR", nhs_as_svc_ia="urn:nhs:names:services:mm:PORX_IN090101UK31"
    )
    return device


@pytest.fixture
def another_device_with_same_key() -> Device:
    org = Root.create_ods_organisation(ods_code="AB123")
    product_team = org.create_product_team(name="Product Team")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="Device-2")
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    return device


@pytest.mark.integration
def test__device_repository_read_by_id(device: Device, repository: DeviceRepository):
    repository.write(device)
    device_from_db = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )
    assert device_from_db.dict() == device.dict()


@pytest.mark.integration
def test__device_repository_read_by_key(device: Device, repository: DeviceRepository):
    repository.write(device)
    device_from_db = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.keys[0].key_value,
    )
    assert device_from_db.dict() == device.dict()


@pytest.mark.integration
def test__device_repository_already_exists(device, repository: DeviceRepository):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(device)


@pytest.mark.integration
def test__device_repository_key_already_exists_on_another_device(
    device, another_device_with_same_key, repository: DeviceRepository
):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(another_device_with_same_key)


def test__device_repository_key_already_exists_on_another_device(
    device, another_device_with_same_key, repository: DeviceRepository
):
    repository.write(device)
    with pytest.raises(AlreadyExistsError):
        repository.write(another_device_with_same_key)


@pytest.mark.integration
def test__device_repository__device_does_not_exist(repository: DeviceRepository):
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id="foo", product_id="bar", id="123")


def test__device_repository_local(device: Device, repository: DeviceRepository):
    repository.write(device)
    device_from_db = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )
    assert device_from_db.dict() == device.dict()


def test__device_repository__device_does_not_exist_local(
    repository: DeviceRepository,
):
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id="foo", product_id="bar", id="123")


@pytest.mark.integration
def test__device_repository__update(device: Device, repository: DeviceRepository):
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )
    intermediate_device.update(name="foo-bar")

    repository.write(intermediate_device)
    time.sleep(1)

    final_device = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )

    assert final_device.name == "foo-bar"

    assert final_device.created_on == device.created_on
    assert final_device.updated_on > device.updated_on


@pytest.mark.integration
def test__device_repository__delete(
    device_with_tag: Device, repository: DeviceRepository
):
    repository.write(device_with_tag)
    time.sleep(1)

    read_query = dict(
        product_team_id=device_with_tag.product_team_id,
        product_id=device_with_tag.product_id,
        id=device_with_tag.id,
    )

    # Retrieve the model and treat this as the initial state
    device = repository.read(**read_query)
    device.delete()
    repository.write(device)
    time.sleep(1)

    # Attempt to read the original device, expecting an ItemNotFound error
    with pytest.raises(ItemNotFound):
        repository.read(**read_query)

    # Read the deleted device
    inactive_repository = InactiveDeviceRepository(
        table_name=repository.table_name, dynamodb_client=repository.client
    )
    deleted_device = inactive_repository.read(**read_query)

    # Assert device is inactive after being deleted
    assert deleted_device is not None
    assert deleted_device.status is Status.INACTIVE
    assert deleted_device.tags == set()
    assert deleted_device.created_on == device_with_tag.created_on
    assert deleted_device.updated_on > device_with_tag.updated_on


@pytest.mark.integration
def test__device_repository__can_delete_second_device_with_same_key(
    repository: DeviceRepository,
):
    org = Root.create_ods_organisation(ods_code="AAA")
    product_team = org.create_product_team(name="MyTeam")
    product = product_team.create_cpm_product(name="Product")
    device = product.create_device(name="OriginalDevice")
    device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
    repository.write(device)
    time.sleep(1)

    read_query = dict(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=DEVICE_KEY,
    )
    repository.read(**read_query)  # passes

    device.clear_events()
    device.delete()
    repository.write(device)
    time.sleep(1)

    with pytest.raises(ItemNotFound):
        repository.read(**read_query)

    inactive_repository = InactiveDeviceRepository(
        table_name=repository.table_name, dynamodb_client=repository.client
    )
    deleted_device = inactive_repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )
    assert deleted_device.status is Status.INACTIVE

    # Can re-add the same product id Key after a previous device is inactive
    for i in range(5):
        _device = product.create_device(name=f"Device-{i}")
        _device.add_key(key_value=DEVICE_KEY, key_type=DeviceKeyType.PRODUCT_ID)
        repository.write(_device)
        time.sleep(1)

        repository.read(**read_query)  # passes

        _device.clear_events()
        _device.delete()
        repository.write(_device)
        time.sleep(1)
        with pytest.raises(ItemNotFound):
            repository.read(**read_query)

        # Assert device is inactive after being deleted
        _deleted_device = inactive_repository.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            id=_device.id,
        )
        assert _deleted_device.status is Status.INACTIVE


@pytest.mark.integration
def test__device_repository__add_key(device: Device, repository: DeviceRepository):
    repository.write(device)

    # Retrieve the model and treat this as the initial state
    intermediate_device = repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=device.id,
    )
    assert len(intermediate_device.keys) == 1

    intermediate_device.add_key(
        key_type=DeviceKeyType.PRODUCT_ID, key_value="P.AAA-CCC"
    )
    repository.write(intermediate_device)
    time.sleep(1)

    # Read the same device multiple times, indexed by key and id
    # to verify that they're all the same
    root_index = intermediate_device.id
    non_root_indexes = [k.key_value for k in intermediate_device.keys]

    retrieved_devices = []
    for key_value in [root_index] + non_root_indexes:
        _device = repository.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            id=key_value,
        ).dict()
        retrieved_devices.append(_device)

    # Assert that there are 2 keys, the device can be retrieved 3 ways from the db,
    # and that all 3 are identical
    assert len(intermediate_device.keys) == 2
    assert len(retrieved_devices) == 3
    assert [retrieved_devices[0]] * 3 == retrieved_devices

    assert retrieved_devices[0]["created_on"] == device.created_on
    assert retrieved_devices[0]["updated_on"] > device.updated_on


@pytest.fixture
def device_created_event():
    return DeviceCreatedEvent(
        id="123",
        name="foo",
        product_team_id="123",
        product_id="123",
        ods_code="abc",
        status="good",
        created_on="123",
        updated_on=None,
        deleted_on=None,
        keys=[],
        tags=["a", "b", "c"],
        questionnaire_responses={"foo": "bar"},
        device_reference_data={},
    )


def test_serialise_data_with_event(device_created_event):
    _serialised_data = compress_device_fields(data=device_created_event)
    _serialised_tags = _serialised_data.pop("tags")

    _data = asdict(device_created_event)
    _tags = _data.pop("tags")

    assert _data == _serialised_data
    assert [pkl_loads_gzip(tag) for tag in pkl_loads_gzip(_serialised_tags)] == _tags


def test_serialise_data_with_dict(device_created_event):
    data = asdict(device_created_event, recurse=False)
    _serialised_data = compress_device_fields(data=deepcopy(data))
    _serialised_tags = _serialised_data.pop("tags")

    _tags = data.pop("tags")

    assert data == _serialised_data
    assert [pkl_loads_gzip(tag) for tag in pkl_loads_gzip(_serialised_tags)] == _tags


def test_serialise_data_with_event_with_other_fields_compressed(device_created_event):
    _serialised_data = compress_device_fields(
        data=device_created_event,
        fields_to_compress=["questionnaire_responses", "status"],
    )
    _serialised_tags = _serialised_data.pop("tags")
    _serialised_responses = _serialised_data.pop("questionnaire_responses")
    _serialised_status = _serialised_data.pop("status")

    _data = asdict(device_created_event)
    _tags = _data.pop("tags")
    _responses = _data.pop("questionnaire_responses")
    _status = _data.pop("status")

    assert _data == _serialised_data
    assert [pkl_loads_gzip(tag) for tag in pkl_loads_gzip(_serialised_tags)] == _tags
    assert pkl_loads_gzip(_serialised_responses) == _responses
    assert pkl_loads_gzip(_serialised_status) == _status
