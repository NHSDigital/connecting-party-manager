"""
In order to reduce human error:
1. All values are uppercase
2. similar characters have been removed from the set of available characters.
  e.g. 0/O/Q, 1/I, S/5, B/8, and Z/2
"""

import random
from datetime import datetime

from .device_key import DeviceKeyType
from .validation import CpmId

PART_LENGTH = 3
N_PARTS = 2


def generate_device_key(device_type: DeviceKeyType) -> str:
    rng = random.Random(datetime.now().timestamp())

    match device_type:
        case DeviceKeyType.PRODUCT_ID:
            device_key = "-".join(
                "".join(rng.choices(CpmId.Product.PRODUCT_ID_CHARS, k=PART_LENGTH))
                for _ in range(N_PARTS)
            )
            return f"P.{device_key}"
