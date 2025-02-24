# from io import BytesIO

# from etl_utils.io import pkl_dump_lz4, pkl_dumps_lz4, pkl_load_lz4
# from etl_utils.io.test.io_utils import pkl_loads_lz4
# from event.json import json_load
# import pytest

# from etl.sds.tests.constants import EtlTestDataPath


# @pytest.mark.s3(EtlTestDataPath.FULL_JSON) Uncomment this when archived
# def test_pkl_lz4(test_data_paths):
#     (path,) = test_data_paths
#     with open(path, "rb") as f:
#         data = json_load(f)

#     buffer = BytesIO()
#     pkl_dump_lz4(fp=buffer, obj=data)
#     buffer.seek(0)
#     assert pkl_load_lz4(fp=buffer) == data


# @pytest.mark.s3(EtlTestDataPath.FULL_JSON) Uncomment this when archived
# def test_pkl_lz4_bytes(test_data_paths):
#     (path,) = test_data_paths
#     with open(path, "rb") as f:
#         data = json_load(f)

#     data_as_bytes = pkl_dumps_lz4(obj=data)
#     assert pkl_loads_lz4(data=data_as_bytes) == data
