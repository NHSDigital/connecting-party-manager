from itertools import chain

from domain.core.device.v2 import Device


def export_events(devices: list[Device]) -> list[dict]:
    """
    Pulls and chains (flattens) the list of events out of each Device.
    The return list of events is enough to reproduce the state of the
    provided devices. This is needed for the transform lambda in "updates"
    mode.
    """
    return list(chain.from_iterable(map(Device.export_events, devices)))


def export_devices(devices: list[Device]) -> list[dict]:
    """
    Serialises the current state of provided devices as dictionaries.
    This is needed for the transform lambda in "bulk" mode.
    """
    _devices = [device.state() for device in devices]
    return _devices
