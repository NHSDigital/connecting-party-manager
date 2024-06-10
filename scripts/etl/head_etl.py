"""
Run with

    poetry run python scripts/etl/head_etl.py
"""

import json
import sys
from functools import partial

import boto3
from changelog.changelog_precommit import PATH_TO_ROOT
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import EtlEncoder, pkl_load_lz4
from mypy_boto3_s3 import S3Client

from test_helpers.aws_session import aws_session
from test_helpers.terraform import read_terraform_output


def _get_object(s3_client: S3Client, bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"]
    except:
        return None


def _ldif_head(s3_client: S3Client, bucket, key):
    head = None
    body = _get_object(s3_client=s3_client, bucket=bucket, key=key)
    if body:
        head, *_ = body.read().split(b"\n\n")
    return head


def _pkl_loads_head(s3_client: S3Client, bucket, key):
    head = None
    body = _get_object(s3_client=s3_client, bucket=bucket, key=key)
    if body:
        items = pkl_load_lz4(body)
        if items:
            head = items[0].decode()
    return head


def main(workspace):
    etl_bucket = (
        f"nhse-cpm--{workspace}--sds--etl"
        if workspace
        else read_terraform_output("sds_etl.value.bucket")
    )

    with aws_session():
        s3_client = boto3.client("s3")
        get_object = partial(_get_object, s3_client=s3_client)
        ldif_head = partial(_ldif_head, s3_client=s3_client)
        pkl_loads_head = partial(_pkl_loads_head, s3_client=s3_client)

        body = get_object(bucket=etl_bucket, key=CHANGELOG_NUMBER)
        changelog_number = body.read().decode() if body else body

        extract_head = ldif_head(bucket=etl_bucket, key=WorkerKey.EXTRACT)
        transform_head = pkl_loads_head(bucket=etl_bucket, key=WorkerKey.TRANSFORM)
        load_head = pkl_loads_head(bucket=etl_bucket, key=WorkerKey.LOAD)

    path = PATH_TO_ROOT / ".downloads" / "etl-head.json"
    with open(path, "w") as f:
        json.dump(
            fp=f,
            obj={
                "changelog_number": changelog_number,
                "extract": extract_head,
                "transform": transform_head,
                "load": load_head,
            },
            cls=EtlEncoder,
            indent=2,
        )
    print("Written to", path)  # noqa


if __name__ == "__main__":
    _, workspace = sys.argv
    main(workspace)
