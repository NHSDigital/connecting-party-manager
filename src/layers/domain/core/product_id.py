"""
In order to reduce human error:
1. All values are uppercase
2. similar characters have been removed from the set of available characters.
  e.g. 0/O/Q, 1/I, S/5, B/8, and Z/2
"""
import random
import re

PRODUCT_ID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"
PRODUCT_ID_REGEX = re.compile(rf"^[{PRODUCT_ID_CHARS}]{{3}}-[{PRODUCT_ID_CHARS}]{{3}}$")

PART_LENGTH = 3
N_PARTS = 2


def generate_product_id(seed: int | None = None) -> str:
    rng = random.Random(seed)
    return "-".join(
        "".join(rng.choices(PRODUCT_ID_CHARS, k=PART_LENGTH)) for _ in range(N_PARTS)
    )
