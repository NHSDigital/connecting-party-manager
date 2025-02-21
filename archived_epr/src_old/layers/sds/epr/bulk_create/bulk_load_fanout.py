from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team.v1 import ProductTeam


def count_indexes(obj: Device | DeviceReferenceData | EprProduct | ProductTeam):
    count = 1
    if isinstance(obj, (Device, EprProduct, ProductTeam)):
        count += len(obj.keys)
    if isinstance(obj, (Device)):
        count += len(obj.tags)
    return count
