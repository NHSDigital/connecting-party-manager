class ItemNotFound(Exception):
    def __init__(self):
        super().__init__("Item could not be found")
