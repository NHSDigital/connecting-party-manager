import os
from abc import ABC

from pydantic import BaseModel


class BaseEnvironment(BaseModel, ABC):
    """
    Automatically parse environmental variables,
    and additionally validate that the members of this model
    have been set. For example, the following will raise an
    error if 'SOMETHING' has not been set in the environment:

        class Environment(BaseEnvironment):
            SOMETHING: str

        Environment.build()
    """

    @classmethod
    def build[Model](cls: type[Model]) -> Model:
        return cls(**os.environ)
