class UnableToUnmarshall(Exception):
    pass


class NotFoundException(Exception):
    def __init__(self, key):
        super().__init__(f"Could not find object with key '{key}'")


class AlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Item already exists")


class UnhandledTransaction(Exception):
    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")
