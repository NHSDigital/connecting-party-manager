from contextlib import contextmanager
from typing import IO, TYPE_CHECKING, Generator

from smart_open import open as _smart_open

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


@contextmanager
def smart_open(
    s3_client: "S3Client", s3_path: str, mode="rb"
) -> Generator[IO, None, None]:
    with _smart_open(s3_path, mode=mode, transport_params={"client": s3_client}) as f:
        yield f
