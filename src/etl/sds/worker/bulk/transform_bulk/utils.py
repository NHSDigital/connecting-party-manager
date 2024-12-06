from contextlib import contextmanager
from typing import TYPE_CHECKING

from etl_utils.smart_open import smart_open

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


@contextmanager
def smart_open_if_exists(s3_client: "S3Client", s3_path: str, empty_content: bytes):
    try:
        with smart_open(s3_client=s3_client, s3_path=s3_path, mode="rb") as f:
            yield f
    except:
        with smart_open(s3_client=s3_client, s3_path=s3_path, mode="wb") as f:
            f.write(empty_content)

        with smart_open(s3_client=s3_client, s3_path=s3_path, mode="rb") as f:
            yield f
