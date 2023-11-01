from .entity import Entity


class User(Entity[str]):
    def __init__(self, id: str, name: str):
        super().__init__(id=id, name=name)
