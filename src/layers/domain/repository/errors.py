from pydantic import BaseModel


class UnableToUnmarshall(Exception):
    pass


class ItemNotFound(Exception):
    def __init__(self, key):
        super().__init__(f"Could not find object with key '{key}'")


class AlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Item already exists")


class UnhandledTransaction(Exception):
    def __init__(
        self, message: str, code: str, unhandled_transactions: list[BaseModel]
    ):
        _unhandled_transactions = "\n".join(map(BaseModel.json, unhandled_transactions))
        super().__init__(f"{code}: {message}\n{_unhandled_transactions}")
