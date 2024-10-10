import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from domain.core.base import BaseModel
from domain.core.device_key.v1 import validate_key
from domain.core.error import InvalidKeyPattern
from domain.core.product_key.v1 import ProductKeyType
from pydantic import validator

FIRST_ASID = 200000099999
FIRST_PARTY_KEY = 849999

PRODUCT_ID_PART_LENGTH = 3
PRODUCT_ID_NUMBER_OF_PARTS: int = 2
PRODUCT_ID_VALID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
PRODUCT_ID_PATTERN = re.compile(
    rf"^P\.[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}-[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}$"
)
PRODUCT_TEAM_ID_PATTERN = re.compile(
    r"^[a-zA-Z0-9]+\.([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})$"
)


class CpmSystemId(BaseModel, ABC):
    __root__: str = None

    @classmethod
    @abstractmethod
    def create(cls, current_number=None, **kwargs):
        """Create a new instance of the ID."""
        pass

    @classmethod
    @abstractmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate the key format."""
        pass

    @property
    def id(self):
        return self.__root__

    @validator("__root__")
    def validate_root(cls, cpm_system_id):
        if not cls.validate_cpm_system_id(cpm_system_id):
            raise ValueError("Invalid cpm system id provided")

        return cpm_system_id

    def __str__(self):
        return self.id


class AsidId(CpmSystemId):

    @classmethod
    def create(cls, current_number: int):
        current_number = current_number or FIRST_ASID
        latest_number = current_number + 1
        return cls(__root__=f"{latest_number:012d}")

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the ASID has the correct format."""
        return (
            cpm_system_id.isdigit()
            and len(cpm_system_id) == 12
            and cpm_system_id.startswith("2")
        )

    @property
    def latest_number(self):
        if self.id:
            return int(self.id)


class PartyKeyId(CpmSystemId):

    @classmethod
    def create(cls, current_number: int, ods_code: str):
        current_number = current_number or FIRST_PARTY_KEY
        latest_number = current_number + 1
        return cls(
            __root__=f"{ods_code}-{latest_number:06d}",
        )

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the party key has the correct format."""
        try:
            validate_key(key=cpm_system_id, type=ProductKeyType.PARTY_KEY)
        except InvalidKeyPattern:
            return False
        return True

    @property
    def latest_number(self):
        if self.id:
            return int(self.id.split("-")[1])


class ProductId(CpmSystemId):
    @classmethod
    def create(cls):
        """No current_id needed, key is generated randomly."""
        rng = random.Random(datetime.now().timestamp())
        product_id = "-".join(
            "".join(rng.choices(PRODUCT_ID_VALID_CHARS, k=PRODUCT_ID_PART_LENGTH))
            for _ in range(PRODUCT_ID_NUMBER_OF_PARTS)
        )
        return cls(__root__=f"P.{product_id}")

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the ProductId has the correct format."""
        return PRODUCT_ID_PATTERN.match(cpm_system_id) is not None


class ProductTeamId(CpmSystemId):
    @classmethod
    def create(cls, ods_code: str):
        return cls(__root__=f"{ods_code}.{uuid4()}")

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the product_team key has the correct format."""
        return PRODUCT_TEAM_ID_PATTERN.match(cpm_system_id) is not None
