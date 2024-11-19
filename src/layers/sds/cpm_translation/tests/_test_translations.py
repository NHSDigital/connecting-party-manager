from unittest import mock
from uuid import uuid4

from domain.core.device.v2 import Device, DeviceType
from domain.core.root.v2 import Root
from sds.cpm_translation.modify_key import NotAnSdsKey
from sds.cpm_translation.translations import modify_devices
from sds.domain.organizational_unit import OrganizationalUnitDistinguishedName
from sds.domain.sds_modification_request import SdsModificationRequest

MOCK_PATH = "sds.cpm_translation.translations.{}"

DUMMY_SDS_MODIFICATION_REQUEST_DATA = dict(
    distinguished_name=OrganizationalUnitDistinguishedName(
        ou="services", o="nhs", uniqueidentifier=""
    ),
    objectclass={"modify"},
    changetype={"add"},
    uniqueidentifier={"123"},
)


def mock_patch(function_name):
    return mock.patch(MOCK_PATH.format(function_name))


@mock_patch("get_modify_key_function")
@mock_patch("update_device_metadata")
def test_modify_devices(mocked_update_device_metadata, mocked_get_modify_key_function):
    class DeviceFactory:
        def __init__(self):
            self.devices: list[Device] = []

        def new_device(self) -> Device:
            org = Root.create_ods_organisation(ods_code="foo")
            product_team = org.create_product_team(id=uuid4(), name="foo")
            device = product_team.create_device(
                name="foo", device_type=DeviceType.PRODUCT
            )
            self.devices.append(device)
            return device

    new_device_factory = DeviceFactory()
    old_device_factory = DeviceFactory()

    def _get_modify_key_function(model, field_name, modification_type):
        if field_name != "nhs_as_client":
            raise NotAnSdsKey
        return lambda devices, field_name, value: devices + [
            new_device_factory.new_device()
        ]

    for _ in range(10):
        old_device_factory.new_device()

    mocked_repository = mock.Mock()
    mocked_repository.query_by_tag.return_value = old_device_factory.devices

    mocked_update_device_metadata.side_effect = (
        lambda device, model, modification_type, field_alias, new_values: device
    )
    mocked_get_modify_key_function.side_effect = _get_modify_key_function

    modified_devices = list(
        modify_devices(
            modification_request=SdsModificationRequest(
                **DUMMY_SDS_MODIFICATION_REQUEST_DATA,
                modifications=[
                    ("add", "nhsasclient", set()),  # key field
                    ("add", "nhsproductname", set()),  # not a key field
                    ("add", "nhsasclient", set()),
                    ("add", "nhsproductname", set()),
                ],
            ),
            repository=mocked_repository,
        )
    )

    assert len(new_device_factory.devices) == 2  # 2 key_field modifications
    assert len(modified_devices) == 12  # 10 original plus 2 new
    assert sorted(modified_devices, key=lambda device: device.id) == sorted(
        old_device_factory.devices + new_device_factory.devices,
        key=lambda device: device.id,
    )
