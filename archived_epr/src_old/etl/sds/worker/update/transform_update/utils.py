from itertools import chain

from domain.core.aggregate_root import AggregateRoot
from domain.core.device import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team.v1 import ProductTeam


def export_events(
    objects: list[ProductTeam | EprProduct | DeviceReferenceData | Device],
):
    """
    Pulls and chains (flattens) the list of events out of each Device.
    The return list of events is enough to reproduce the state of the
    provided devices. This is needed for the transform lambda in "updates"
    mode.
    """
    return list(
        chain.from_iterable(map(AggregateRoot.export_events, filter(None, objects)))
    )
