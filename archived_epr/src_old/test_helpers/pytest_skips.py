"""Define CI pytest skip markers here"""

import os

import pytest

memory_intensive = pytest.mark.skipif(
    condition=os.environ.get("CI") is not None,
    reason="Requires too much memory for CI",
)

long_running = pytest.mark.skipif(
    condition=os.environ.get("ALL") is None,
    reason="Takes too long to run",
)
