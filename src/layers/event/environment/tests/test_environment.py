import os
from unittest import mock

from event.environment import BaseEnvironment


def test_base_environment():
    class Environment(BaseEnvironment):
        FOO: str

    with mock.patch.dict(os.environ, {"FOO": "foo!", "BAR": "bar!"}):
        env = Environment.build()
    assert hasattr(env, "FOO")
    assert not hasattr(env, "BAR")
    assert env.FOO == "foo!"
