import json
from codecs import getwriter
from collections import deque
from io import BytesIO
from uuid import UUID


class EtlEncoder(json.JSONEncoder):
    """Serialise sets to a sorted list"""

    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, deque):
            return list(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def json_dump_bytes(fp: BytesIO, obj: list | dict):
    StreamWriter = getwriter("utf-8")
    return json.dump(fp=StreamWriter(fp), obj=obj, cls=EtlEncoder)
