import os
from abc import ABC
from typing import TypeVar

from pydantic import BaseModel

Model = TypeVar("Model")


class BaseEnvironment(BaseModel, ABC):
    """
    Automatically parse environmental variables,
    and additionally validate that the members of this model
    have been set. For example, the following will raise an
    error if 'SOMETHING' has not been set in the environment:

        class Environment(BaseEnvironment):
            SOMETHING: str

        Environment.model_construct()
    """

    @classmethod
    def build(cls: Model) -> Model:
        return cls(**os.environ)
