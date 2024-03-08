"""
Run with

    poetry run python scripts/etl/clear_state_inputs.py
"""

import json

import boto3
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey

from test_helpers.aws_session import aws_session
from test_helpers.terraform import read_terraform_output

EXPECTED_CHANGELOG_NUMBER = "0"
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = json.dumps([]).encode()


def main():
    etl_bucket = read_terraform_output("sds_etl.value.bucket")

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


if __name__ == "__main__":
    main()
