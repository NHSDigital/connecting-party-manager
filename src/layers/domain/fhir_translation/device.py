from domain.core.device import Device as DomainDevice
from domain.core.product_team import ProductTeam
from domain.fhir.r4 import Device as FhirDevice
from domain.fhir.r4 import StrictDevice as StrictFhirDevice
from domain.fhir.r4.cpm_model import SYSTEM
from domain.fhir.r4.cpm_model import Device as CpmFhirDevice
from domain.fhir.r4.cpm_model import (
    DeviceDefinitionIdentifier,
    DeviceDefinitionReference,
    DeviceIdentifier,
    DeviceName,
    DeviceOwnerReference,
    ProductTeamIdentifier,
)
from domain.fhir_translation.parse import create_fhir_model_from_fhir_json
from event.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_fhir_device_json(fhir_device_json: dict) -> CpmFhirDevice:
    fhir_device = create_fhir_model_from_fhir_json(
        fhir_json=fhir_device_json,
        fhir_models=[FhirDevice, StrictFhirDevice],
        our_model=CpmFhirDevice,
    )
    return fhir_device


def create_domain_device_from_fhir_device(
    fhir_device: CpmFhirDevice, product_team: ProductTeam
) -> DomainDevice:
    (device_name,) = fhir_device.deviceName
    device = product_team.create_device(
        name=device_name.name,
        type=fhir_device.definition.identifier.value,
    )
    for identifier in fhir_device.identifier:
        device.add_key(type=identifier.key_type, key=identifier.value)
    return device


def create_fhir_model_from_device(device: DomainDevice) -> CpmFhirDevice:
    return CpmFhirDevice(
        resourceType=CpmFhirDevice.__name__,
        deviceName=[DeviceName(name=device.name)],
        definition=DeviceDefinitionReference(
            identifier=DeviceDefinitionIdentifier(value=device.type)
        ),
        identifier=[
            DeviceIdentifier(system=f"{SYSTEM}/{key.type}", value=key.key)
            for key in device.keys.values()
        ],
        owner=DeviceOwnerReference(
            identifier=ProductTeamIdentifier(value=device.product_team_id)
        ),
    )
