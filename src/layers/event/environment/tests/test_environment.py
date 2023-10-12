import os
from unittest import mock

from event.environment import BaseEnvironment


def test_base_environment():
    class Environment(BaseEnvironment):
        FOO: str

    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        env = Environment.model_construct()
    assert env.FOO == "bar"
