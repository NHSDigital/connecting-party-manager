import os
import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cache
from pathlib import Path
from uuid import uuid4

from domain.core.base import BaseModel
from domain.core.error import InvalidKeyPattern
from domain.core.product_key import ProductKeyType
from domain.core.product_team_key import validate_key
from event.json import json_load
from pydantic import validator

FIRST_ASID = 200000099999
FIRST_PARTY_KEY = 849999

PRODUCT_ID_PART_LENGTH = 3
PRODUCT_ID_NUMBER_OF_PARTS: int = 2
PRODUCT_ID_VALID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
PRODUCT_ID_PATTERN = re.compile(
    rf"^P\.[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}-[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}$"
)

PATH_TO_CPM_SYSTEM_IDS = Path(__file__).parent
PRODUCT_IDS_GENERATED_FILE = f"{PATH_TO_CPM_SYSTEM_IDS}/generated_ids/product_ids.json"
PRODUCT_TEAM_EPR_ID_PATTERN = re.compile(
    r"^[a-zA-Z0-9]+\.([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})$"
)
PRODUCT_TEAM_ID_PATTERN = re.compile(
    r"^([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})$"
)


@cache
def _load_existing_ids():
    if os.path.exists(PRODUCT_IDS_GENERATED_FILE):
        with open(PRODUCT_IDS_GENERATED_FILE, "r") as file:
            return set(json_load(file))
    return set()


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
            validate_key(key_value=cpm_system_id, key_type=ProductKeyType.PARTY_KEY)
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
        if f"P.{product_id}" in cls.load_existing_ids():
            return cls.create()
        return cls(__root__=f"P.{product_id}")

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the ProductId has the correct format."""
        return PRODUCT_ID_PATTERN.match(cpm_system_id) is not None

    @classmethod
    def load_existing_ids(cls):
        return _load_existing_ids()


class ProductTeamId(CpmSystemId):
    @classmethod
    def create(cls, ods_code: str = None):
        if ods_code:
            return cls(__root__=f"{ods_code}.{uuid4()}")
        return cls(__root__=str(uuid4()))

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the product_team key has the correct format."""
        if "." in cpm_system_id:
            return PRODUCT_TEAM_EPR_ID_PATTERN.match(cpm_system_id) is not None
        return PRODUCT_TEAM_ID_PATTERN.match(cpm_system_id) is not None
