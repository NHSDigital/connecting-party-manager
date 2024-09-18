import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum, auto
from typing import Optional

from domain.core.base import BaseModel


class CpmSystemIdType(StrEnum):
    ASIDNUMBER = auto()
    PARTYKEYNUMBER = auto()
    PRODUCTID = auto()


class CpmSystemId(BaseModel, ABC):
    key_name: str
    id: str

    @classmethod
    @abstractmethod
    def create(cls, current_number=None, **kwargs):
        """Create a new instance of the ID."""
        instance = cls(key_name="", id="")
        return instance

    @abstractmethod
    def _format_key(self, **kwargs) -> str:
        """Format the key according to the specific ID rules."""
        pass

    @classmethod
    @abstractmethod
    def validate_key(cls, key: str) -> bool:
        """Validate the key format."""
        pass


class AsidId(CpmSystemId):
    latest_number: Optional[int]

    @classmethod
    def create(cls, current_number=None):
        current_number = (
            current_number.get("latest") if current_number else 200000099999
        )
        instance = super().create(
            current_number=current_number, key_name=CpmSystemIdType.ASIDNUMBER
        )
        instance.latest_number = current_number + 1  # Increment current_id
        instance.id = cls._format_key(cls, instance.latest_number)
        return instance

    def _format_key(cls, latest_number: int) -> str:
        """Return the ASID as a 12-digit number."""
        return f"{latest_number:012d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ASID has the correct format."""
        return key.isdigit() and len(key) == 12 and key.startswith("2")


class PartyKeyId(CpmSystemId):
    ods_code: str
    latest_number: Optional[int]

    @classmethod
    def create(cls, current_number=None, ods_code=""):
        current_number = current_number.get("latest") if current_number else 849999
        instance = cls(
            key_name=CpmSystemIdType.PARTYKEYNUMBER, id="", ods_code=ods_code
        )
        instance.latest_number = current_number + 1
        instance.id = cls._format_key(
            cls=cls, ods_code=ods_code, latest_number=instance.latest_number
        )
        return instance

    def _format_key(cls, ods_code: str, latest_number: int) -> str:
        """Format the party key with the ODS code and a 7-digit number."""
        return f"{ods_code}-{latest_number:06d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the party key has the correct format."""
        parts = key.split("-")
        if len(parts) != 2:
            return False
        ods_code, number = parts
        return ods_code.isalpha() and number.isdigit() and len(number) == 6


class ProductId(CpmSystemId):
    length: int = 3
    n_parts: int = 2
    valid_chars: str = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret

    @classmethod
    def create(cls):
        """No current_id needed, key is generated randomly."""
        instance = super().create(key_name=CpmSystemIdType.PRODUCTID)
        rng = random.Random(datetime.now().timestamp())
        product_id = "-".join(
            "".join(rng.choices(instance.valid_chars, k=instance.length))
            for _ in range(instance.n_parts)
        )
        instance.id = instance._format_key(product_id)
        return instance

    def _format_key(cls, product_id) -> str:
        """Generate the product ID as a random string in the format 'P.XXX-XXX'."""
        return f"P.{product_id}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ProductId has the correct format."""
        instance = super().create()

        ID_PATTERN = re.compile(
            rf"^P\.[{instance.valid_chars}]{{3}}-[{instance.valid_chars}]{{3}}$"
        )
        return bool(ID_PATTERN.match(key))
