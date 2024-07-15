"""
Run with

    poetry run python scripts/etl/head_etl.py
"""

import json
import sys
from dataclasses import asdict, dataclass
from functools import partial

import boto3
from changelog.changelog_precommit import PATH_TO_ROOT
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import EtlEncoder, pkl_load_lz4
from mypy_boto3_s3 import S3Client

from test_helpers.aws_session import aws_session
from test_helpers.terraform import read_terraform_output

PATH_TO_ETL_HEAD = PATH_TO_ROOT / ".downloads" / "etl-head.json"
BUCKET = "nhse-cpm--{workspace}--sds--etl"


@dataclass(kw_only=True)
class EtlHead:
    changelog_number: str
    extract: dict
    transform: dict
    load: dict


def _get_object(s3_client: S3Client, bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"]
    except:
        return None


def _get_changelog_number(s3_client: S3Client, bucket):
    body = _get_object(s3_client=s3_client, bucket=bucket, key=CHANGELOG_NUMBER)
    return body.read().decode() if body else body


def _ldif_head(s3_client: S3Client, bucket, key):
    head = None
    body = _get_object(s3_client=s3_client, bucket=bucket, key=key)
    if body:
        head, *_ = body.read().split(b"\n\n")
        head = head.decode()
    return head


def _pkl_loads_head(s3_client: S3Client, bucket, key):
    head = {}
    body = _get_object(s3_client=s3_client, bucket=bucket, key=key)
    if body:
        items = pkl_load_lz4(body)
        if items:
            head = items[0]
    return head


def _get_etl_head(bucket) -> EtlHead:
    s3_client = boto3.client("s3")

    get_changelog_number = partial(_get_changelog_number, s3_client=s3_client)
    ldif_head = partial(_ldif_head, s3_client=s3_client)
    pkl_loads_head = partial(_pkl_loads_head, s3_client=s3_client)

    changelog_number = get_changelog_number(bucket=bucket)
    extract_head = ldif_head(bucket=bucket, key=WorkerKey.EXTRACT)
    transform_head = pkl_loads_head(bucket=bucket, key=WorkerKey.TRANSFORM)
    load_head = pkl_loads_head(bucket=bucket, key=WorkerKey.LOAD)

    return EtlHead(
        changelog_number=changelog_number,
        extract=extract_head,
        transform=transform_head,
        load=load_head,
    )


def main(workspace):
    if workspace:
        etl_bucket = BUCKET.format(workspace=workspace)
        etl_head = _get_etl_head(bucket=etl_bucket)
    else:
        with aws_session():
            etl_bucket = read_terraform_output("sds_etl.value.bucket")
            etl_head = _get_etl_head(bucket=etl_bucket)

    with open(PATH_TO_ETL_HEAD, "w") as f:
        json.dump(fp=f, obj=asdict(etl_head), cls=EtlEncoder, indent=2)

    print("Written to", PATH_TO_ETL_HEAD)  # noqa


if __name__ == "__main__":
    _, workspace = sys.argv
    main(workspace)
