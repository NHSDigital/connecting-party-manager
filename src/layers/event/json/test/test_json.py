from tempfile import TemporaryFile

import pytest
from event.json import json_load, json_loads
from event.json.errors import DuplicateKeyError


def test_dict_raise_on_duplicates_loads():
    with pytest.raises(DuplicateKeyError):
        json_loads('{"a": "foo", "a": "bar"}')


def test_dict_raise_on_duplicates_load():
    with TemporaryFile() as f:
        f.write(b'{"a": "foo", "a": "bar"}')
        f.seek(0)
        with pytest.raises(DuplicateKeyError):
            json_load(f)
