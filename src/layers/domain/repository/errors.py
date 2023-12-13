class UnableToUnmarshall(Exception):
    pass


class ItemNotFound(Exception):
    def __init__(self, key):
        super().__init__(f"Could not find object with key '{key}'")
