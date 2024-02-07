import json
from codecs import getwriter
from io import BytesIO


class SetEncoder(json.JSONEncoder):
    """Serialise sets to a sorted list"""

    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        return json.JSONEncoder.default(self, obj)


def json_dump_bytes(fp: BytesIO, obj: list | dict):
    StreamWriter = getwriter("utf-8")
    return json.dump(fp=StreamWriter(fp), obj=obj, cls=SetEncoder)
