import json
import pickle
from collections import deque
from io import BytesIO
from typing import IO
from uuid import UUID

import lz4.frame


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


def pkl_dump_lz4(fp: IO, obj):
    with lz4.frame.open(fp, mode="wb") as file:
        pickle.dump(file=file, obj=obj)


def pkl_load_lz4(fp: IO):
    with lz4.frame.open(fp, mode="r") as file:
        return pickle.load(file=file)


def pkl_dumps_lz4(obj):
    fp = BytesIO()
    pkl_dump_lz4(fp=fp, obj=obj)
    return fp.getvalue()
