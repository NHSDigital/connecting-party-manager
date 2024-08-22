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
