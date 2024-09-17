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
    latest_id: str

    @classmethod
    @abstractmethod
    def create(cls, current_id=None, **kwargs):
        """Create a new instance of the ID."""
        instance = cls(key_name=cls._get_key_name(), latest_id="")
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

    @classmethod
    @abstractmethod
    def _get_key_name(cls) -> CpmSystemIdType:
        """Return the key name for the system ID."""
        pass


class AsidId(CpmSystemId):
    latest: Optional[int]

    @classmethod
    def create(cls, current_id=None):
        current_id = current_id.get("latest") if current_id else 200000099999
        instance = super().create(current_id=current_id)
        instance.latest = current_id + 1
        instance.latest_id = cls._format_key(current_id + 1)  # Increment current_id
        return instance

    @classmethod
    def _get_key_name(cls) -> CpmSystemIdType:
        return CpmSystemIdType.ASIDNUMBER

    @staticmethod
    def _format_key(latest_id: int) -> str:
        """Return the ASID as a 12-digit number."""
        return f"{latest_id:012d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ASID has the correct format."""
        return key.isdigit() and len(key) == 12 and key.startswith("2")


class PartyKeyId(CpmSystemId):
    ods_code: str
    latest: Optional[int]

    @classmethod
    def create(cls, current_id=None, ods_code=""):
        current_id = current_id.get("latest") if current_id else 849999
        instance = cls(key_name=cls._get_key_name(), latest_id="", ods_code=ods_code)
        instance.latest = current_id + 1
        instance.latest_id = cls._format_key(
            ods_code=ods_code, latest_id=current_id + 1
        )
        return instance

    @classmethod
    def _get_key_name(cls) -> CpmSystemIdType:
        return CpmSystemIdType.PARTYKEYNUMBER

    @staticmethod
    def _format_key(ods_code: str, latest_id: int) -> str:
        """Format the party key with the ODS code and a 7-digit number."""
        return f"{ods_code}-{latest_id:06d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the party key has the correct format."""
        parts = key.split("-")
        if len(parts) != 2:
            return False
        ods_code, number = parts
        return ods_code.isalpha() and number.isdigit() and len(number) == 6


class ProductId(CpmSystemId):
    length: Optional[int]  # Length of each part of the ID
    n_parts: Optional[int]  # Number of parts in the ID
    valid_chars: Optional[str]  # Valid characters for the ID

    @classmethod
    def create(cls):
        cls.length = 3
        cls.n_parts = 2
        cls.valid_chars = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
        """No current_id needed, key is generated randomly."""
        instance = super().create()
        instance.latest_id = cls._format_key()
        return instance

    @classmethod
    def _get_key_name(cls) -> CpmSystemIdType:
        return CpmSystemIdType.PRODUCTID

    @classmethod
    def _format_key(cls) -> str:
        """Generate the product ID as a random string in the format 'P.XXX-XXX'."""
        rng = random.Random(datetime.now().timestamp())
        device_key = "-".join(
            "".join(rng.choices(cls.valid_chars, k=cls.length))
            for _ in range(cls.n_parts)
        )
        return f"P.{device_key}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate that the ProductId has the correct format."""
        cls.valid_chars = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
        ID_PATTERN = re.compile(
            rf"^P\.[{cls.valid_chars}]{{3}}-[{cls.valid_chars}]{{3}}$"
        )
        return bool(ID_PATTERN.match(key))
