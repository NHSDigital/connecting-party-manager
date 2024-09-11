from abc import abstractmethod

from domain.core.base import BaseModel


class CpmSystemId(BaseModel):
    key_name: str
    latest: int
    current_number: int
    latest_id: str

    @classmethod
    def create(cls, key_name: str, current_id: int):
        # Initialize current_number
        instance = cls(
            key_name=key_name,
            latest=current_id + 1,
            current_number=current_id,
            latest_id="",
        )
        instance.latest_id = instance._format_key()
        return instance

    @abstractmethod
    def _format_key(self) -> str:
        pass

    @abstractmethod
    def validate_key(self, key: str) -> bool:
        pass


class AsidId(CpmSystemId):
    @classmethod
    def create(cls, current_id=None):
        # Initialize current_id with a default if not provided
        current_id = current_id["latest"] if current_id is not None else 200000099999
        return super().create(key_name="ASIDNUMBER", current_id=current_id)

    def _format_key(self) -> str:
        """
        return the asid as a 12-digit number.
        """
        return f"{self.latest:012d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """
        Validate that the ASID has the correct format.
        """
        return key.isdigit() and len(key) == 12 and key.startswith("2")


class PartyKeyId(CpmSystemId):
    ods_code: str

    @classmethod
    def create(cls, current_id=None, ods_code: str = ""):
        # Initialize current_id with a default if not provided
        current_id = current_id["latest"] if current_id is not None else 849999
        instance = cls(
            key_name="PARTYNUMBER",
            current_number=current_id,
            latest=current_id + 1,
            ods_code=ods_code,
            latest_id="",  # Temporary placeholder for latest_id
        )
        instance.latest_id = instance._format_key()
        return instance

    def _format_key(self) -> str:
        """
        Format the party key with the ODS code and a 7-digit number.
        """
        return f"{self.ods_code}-{self.latest:06d}"

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """
        Validate that the party key has the correct format.
        """
        parts = key.split("-")
        if len(parts) != 2:
            return False
        ods_code, number = parts
        return ods_code.isalpha() and number.isdigit() and len(number) == 6
