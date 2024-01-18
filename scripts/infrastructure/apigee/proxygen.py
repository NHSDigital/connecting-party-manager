import os
import sys
from contextlib import contextmanager


@contextmanager
def temporary_home():
    """
    Proxygen expects to find a '.proxygen' folder in the HOME
    directory, so in order to be able to deploy to both prod and
    non-prod (two "homes") we patch HOME from DOT_PROXYGEN
    """
    original_environ = os.environ.copy()
    os.environ["HOME"] = os.environ["DOT_PROXYGEN"]
    yield
    os.environ["HOME"] = original_environ["HOME"]


if __name__ == "__main__":
    with temporary_home():
        from proxygen_cli.cli.command_main import main

        sys.exit(main())
