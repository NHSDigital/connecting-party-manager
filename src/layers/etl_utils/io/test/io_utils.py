from io import BytesIO

from etl_utils.io import pkl_load_lz4


def pkl_loads_lz4(data: bytes):
    return pkl_load_lz4(fp=BytesIO(data))
