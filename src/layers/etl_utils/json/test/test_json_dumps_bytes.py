from io import BytesIO

from etl_utils.json import json_dump_bytes
from event.json import json_loads


def test_json_dump_bytes():
    data = {"foo": "FOO"}
    buffer = BytesIO()
    json_dump_bytes(fp=buffer, obj=data)
    assert json_loads(buffer.getvalue()) == data
