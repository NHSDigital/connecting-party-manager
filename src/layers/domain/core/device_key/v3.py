from abc import ABC, abstractmethod

from domain.repository.repository.tests.model import MyModel
from domain.repository.repository.v3 import Repository
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output


class InitialPartyKeyDoesNotExistError(Exception):
    """
    Custom exception raised when the PARTYKEYNUMBER entry is not found in the database.
    """

    def __init__(
        self, message="Initial party key number doesn't exist in the database"
    ):
        self.message = message
        super().__init__(self.message)


class KeyGenerator(ABC):
    def __init__(self, key_name: str):
        self.key_name = key_name
        self.current_number = self.get_current_number()

    def get_current_number(self) -> int:
        """
        Get latest key number from database
        """
        try:
            repository = Repository(
                table_name=read_terraform_output("dynamodb_table_name.value"),
                model=MyModel,
                dynamodb_client=dynamodb_client(),
            )
            key_value = repository.read(self.key_name)
            return key_value["latest"]
        except KeyError:
            raise InitialPartyKeyDoesNotExistError()

    def generate_key(self) -> str:
        """
        Generate a new key.
        Takes a current number and returns the next consequtive number.
        Updates the existing key in the db.
        """
        self.current_number += 1
        new_key = self._format_key()

        # Write new current number back to database
        self.update_current_number_in_db()
        return new_key

    def update_current_number_in_db(self):
        client = dynamodb_client()

        table_name = read_terraform_output("dynamodb_table_name.value")
        client.update_item(
            TableName=table_name,
            Key={
                "pk": {"S": f"{self.key_name}"},
                "sk": {"S": f"{self.key_name}"},
            },
            UpdateExpression="SET latest = :new_value",
            ExpressionAttributeValues={
                ":new_value": {"N": str(self.current_number)},
            },
        )

    @abstractmethod
    def validate_key(self, key: str) -> bool:
        pass

    @abstractmethod
    def _format_key(self) -> str:
        pass


class PartyKeyGenerator(KeyGenerator):
    def __init__(self, ods_code: str):
        self.ods_code = ods_code
        super().__init__(key_name="PARTYKEYNUMBER")

    def _format_key(self) -> str:
        """
        Format the party key with the ODS code and a 7-digit number.
        """
        return f"{self.ods_code}-{self.current_number:07d}"

    def validate_key(self, key: str) -> bool:
        """
        Validate that the party key has the correct format.
        """
        parts = key.split("-")
        if len(parts) != 2:
            return False
        ods_code, number = parts
        return ods_code.isalpha() and number.isdigit() and len(number) == 7


class ASIDGenerator(KeyGenerator):
    def __init__(self):
        super().__init__(key_name="ASIDNUMBER")

    def _format_key(self) -> str:
        """
        Format the ASID as a consecutive 5-digit number.
        """
        return f"{self.current_number:05d}"

    def validate_key(self, key: str) -> bool:
        """
        Validate that the ASID has the correct format.
        """
        return key.isdigit() and len(key) == 5
