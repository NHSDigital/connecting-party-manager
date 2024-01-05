import pytest
from domain.core.device import Device
from domain.core.root import Root
from domain.fhir.r4.cpm_model import Device as CpmDevice
from domain.fhir_translation.device import (
    create_domain_device_from_fhir_device,
    create_fhir_model_from_device,
    parse_fhir_device_json,
)

from test_helpers.sample_data import DEVICE, FAILED_DEVICE


def test_device_translation():
    """
    Tests that 'create_domain_device_from_fhir_device'
    is the compliment of 'create_fhir_model_from_device'
    """
    fhir_json = DEVICE
    fhir_device = parse_fhir_device_json(fhir_device_json=fhir_json)
    assert isinstance(fhir_device, CpmDevice)

    org = Root.create_ods_organisation(ods_code="F5HIR")
    product_team = org.create_product_team(
        id=fhir_device.owner.identifier.value,
        name="My Product Team",
    )
    device = create_domain_device_from_fhir_device(
        fhir_device=fhir_device, product_team=product_team
    )
    assert isinstance(device, Device)

    fhir_model = create_fhir_model_from_device(device=device)
    assert isinstance(fhir_model, CpmDevice)
    assert fhir_model == fhir_device
    assert fhir_model.dict() == fhir_json


def test_device_translation_failure():
    """
    Tests that 'create_domain_device_from_fhir_device'
    is the compliment of 'create_fhir_model_from_device'
    """
    fhir_json = FAILED_DEVICE
    with pytest.raises(ValueError):
        parse_fhir_device_json(fhir_device_json=fhir_json)
