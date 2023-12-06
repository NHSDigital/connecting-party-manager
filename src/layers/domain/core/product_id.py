"""
The Product Id is a human readable identifier presented in the form of 3 x 3
letter alphanumeric words. e.g. XXX-XXX-XXX.

In order to reduce human error:
1. All values are uppercase
2. similar characters have been removed from the set of available characters.
  e.g. 0/O/Q, 1/I, S/5, B/8, and Z/2

This leaves 26+10-11 = 25 unique characters
9 characters per id gives 3.8 billion unique values: 25^9 = 3,814,697,265,625
"""
import random
import re

PRODUCT_ID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"
PRODUCT_ID_REGEX = (
    f"^[{PRODUCT_ID_CHARS}]{{3}}-[f{PRODUCT_ID_CHARS}]{{3}}-[{PRODUCT_ID_CHARS}]{{3}}$"
)


class InvalidProductIdError(Exception):
    pass


class ProductId(str):
    """
    ProductId has been derived from `str` to allow for string comparisons and
    hashing without having to make any specific changes.
    """

    def __new__(cls, content):
        if not re.match(PRODUCT_ID_REGEX, content):
            raise InvalidProductIdError(f"Invalid Product Id: {content}")
        return str.__new__(cls, content)

    @staticmethod
    def generate(seed: int | None = None) -> "ProductId":
        rng = random.Random(seed)
        return "-".join("".join(rng.choices(PRODUCT_ID_CHARS, k=3)) for _ in range(3))
