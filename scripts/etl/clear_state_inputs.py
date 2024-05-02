"""
Run with

    poetry run python scripts/etl/clear_state_inputs.py
"""

import sys
from collections import deque

import boto3
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import pkl_dumps_lz4

from test_helpers.aws_session import aws_session
from test_helpers.terraform import read_terraform_output

EXPECTED_CHANGELOG_NUMBER = "0"
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = pkl_dumps_lz4(deque())


def main(changelog_number, workspace):
    etl_bucket = (
        f"nhse-cpm--{workspace}--sds--etl"
        if workspace
        else read_terraform_output("sds_etl.value.bucket")
    )

    with aws_session():
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=etl_bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA
        )
        s3_client.put_object(
            Bucket=etl_bucket, Key=WorkerKey.TRANSFORM, Body=EMPTY_JSON_DATA
        )
        s3_client.put_object(
            Bucket=etl_bucket, Key=WorkerKey.LOAD, Body=EMPTY_JSON_DATA
        )
        s3_client.delete_object(Bucket=etl_bucket, Key=CHANGELOG_NUMBER)

    if changelog_number:
        s3_client.put_object(
            Bucket=etl_bucket, Key=CHANGELOG_NUMBER, Body=changelog_number
        )


if __name__ == "__main__":
    _, changelog_number, workspace = sys.argv
    main(changelog_number, workspace)
