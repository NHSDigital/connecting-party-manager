import os
import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cache
from pathlib import Path
from uuid import uuid4

from domain.core.base import BaseModel
from event.json import json_load
from pydantic import validator

PRODUCT_ID_PART_LENGTH = 3
PRODUCT_ID_NUMBER_OF_PARTS: int = 2
PRODUCT_ID_VALID_CHARS = "ACDEFGHJKLMNPRTUVWXY34679"  # pragma: allowlist secret
PRODUCT_ID_PATTERN = re.compile(
    rf"^P\.[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}-[{PRODUCT_ID_VALID_CHARS}]{{{PRODUCT_ID_PART_LENGTH}}}$"
)

PATH_TO_CPM_SYSTEM_IDS = Path(__file__).parent
PRODUCT_IDS_GENERATED_FILE = f"{PATH_TO_CPM_SYSTEM_IDS}/generated_ids/product_ids.json"
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
    def create(cls):
        return cls(__root__=str(uuid4()))

    @classmethod
    def validate_cpm_system_id(cls, cpm_system_id: str) -> bool:
        """Validate that the product_team key has the correct format."""
        return PRODUCT_TEAM_ID_PATTERN.match(cpm_system_id) is not None
