from math import ceil

from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam

FANOUT = 10


def count_indexes(obj: Device | DeviceReferenceData | CpmProduct | ProductTeam):
    count = 1
    if isinstance(obj, (Device, CpmProduct, ProductTeam)):
        count += len(obj.keys)
    if isinstance(obj, (Device)):
        count += len(obj.tags)
    return count


def calculate_batch_size(sequence: list, n_batches: int) -> int:
    return ceil(len(sequence) / (n_batches)) or 1
