import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum, auto

from domain.core.base import BaseModel


class CpmSystemIdType(StrEnum):
    ASID_NUMBER = auto()
    PARTY_KEY_NUMBER = auto()
    PRODUCT_ID = auto()


FIRST_ASID = 200000099999
FIRST_PARTY_KEY = 849999

PRODUCT_ID_PART_LENGTH = 3
PRODUCT_ID_NUMBER_OF_PARTS: int = 2
PRODUCT_ID_VALID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
PRODUCT_ID_PATTERN = re.compile(
    rf"^P\.[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}-[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}$"
)


class CpmSystemId(BaseModel, ABC):
    key_name: str = None
    id: str = None

    @classmethod
    @abstractmethod
    def create(cls, current_number=None, **kwargs):
        """Create a new instance of the ID."""
        pass

    @classmethod
    @abstractmethod
    def validate_key(cls, key: str) -> bool:
        """Validate the key format."""
        pass


class AsidId(CpmSystemId):
    latest_number: int = None

    @classmethod
    def create(cls, current_number: int):
        current_number = current_number or FIRST_ASID
        latest_number = current_number + 1
        id = f"{latest_number:012d}"
        return cls(
            key_name=CpmSystemIdType.ASID_NUMBER, id=id, latest_number=latest_number
        )

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ASID has the correct format."""
        return key.isdigit() and len(key) == 12 and key.startswith("2")


class PartyKeyId(CpmSystemId):
    ods_code: str = None
    latest_number: int = None

    @classmethod
    def create(cls, current_number: int, ods_code: str):
        current_number = current_number or FIRST_PARTY_KEY
        latest_number = current_number + 1
        return cls(
            key_name=CpmSystemIdType.PARTY_KEY_NUMBER,
            id=f"{ods_code}-{latest_number:06d}",
            ods_code=ods_code,
            latest_number=latest_number,
        )

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the party key has the correct format."""
        parts = key.split("-")
        if len(parts) != 2:
            return False
        ods_code, number = parts
        return ods_code.isalpha() and number.isdigit() and len(number) == 6


class ProductId(CpmSystemId):
    @classmethod
    def create(cls):
        """No current_id needed, key is generated randomly."""
        rng = random.Random(datetime.now().timestamp())
        product_id = "-".join(
            "".join(rng.choices(PRODUCT_ID_VALID_CHARS, k=PRODUCT_ID_PART_LENGTH))
            for _ in range(PRODUCT_ID_NUMBER_OF_PARTS)
        )
        return cls(key_name=CpmSystemIdType.PRODUCT_ID, id=f"P.{product_id}")

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ProductId has the correct format."""
        return PRODUCT_ID_PATTERN.match(key) is not None
