import gzip
import pickle
from base64 import b64decode, b64encode
from io import BytesIO


def pkl_loads_gzip(data: str):
    _compressed = b64decode(data.encode())
    with gzip.open(BytesIO(_compressed), mode="r") as file:
        return pickle.load(file=file)


def pkl_dumps_gzip(obj):
    fp = BytesIO()
    with gzip.open(fp, mode="wb") as file:
        pickle.dump(file=file, obj=obj)
    _compressed = fp.getvalue()
    return b64encode(_compressed).decode()
