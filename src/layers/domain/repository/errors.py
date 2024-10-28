from pydantic import BaseModel


class UnableToUnmarshall(Exception):
    pass


class ItemNotFound(Exception):
    def __init__(self, *key_parts: str, item_type: type):
        key = ", ".join(f"'{k}'" for k in key_parts)
        super().__init__(f"Could not find {item_type.__name__} for key ({key})")


class AlreadyExistsError(Exception):
    def __init__(self, msg=None):
        super().__init__(msg or "Item already exists")


class UnhandledTransaction(Exception):
    def __init__(
        self, message: str, code: str, unhandled_transactions: list[BaseModel]
    ):
        _unhandled_transactions = "\n".join(
            item.json(exclude_none=True) for item in unhandled_transactions
        )
        super().__init__(f"{code}: {message}\n{_unhandled_transactions}")
