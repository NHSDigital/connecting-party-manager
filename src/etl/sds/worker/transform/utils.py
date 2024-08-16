from itertools import chain

from domain.core.device.v2 import Device


def export_events(devices: list[Device]) -> list[dict]:
    return list(chain.from_iterable(map(Device.export_events, devices)))


def export_devices(devices: list[Device]):
    _devices = [device.state() for device in devices]
    return _devices
