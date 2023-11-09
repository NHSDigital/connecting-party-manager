from typing import Generic, TypeVar

from .errors import ItemNotFound
from .model import BaseModel

TableItemType = TypeVar("TableItemType", bound=BaseModel)


class Repository(Generic[TableItemType]):
    def __init__(self, model: type[TableItemType]):
        self.model = model

    def create(self, data: dict):
        instance = self.model(**data)
        condition = self.model.pk.does_not_exist() & self.model.sk.does_not_exist()
        return instance.save(condition=condition)

    def read(self, pk, sk=None) -> TableItemType:
        range_key_condition = (self.model.sk == sk) if sk else None
        response = self.model.query(
            hash_key=pk, range_key_condition=range_key_condition
        )

        try:
            (item,) = response
        except ValueError:
            raise ItemNotFound() from None

        return item
