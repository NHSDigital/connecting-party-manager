import os
from unittest import mock

import boto3
import pytest
from moto import mock_aws

TRUSTSTORE_BUCKET = "my-bucket"


def test_update():
    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=TRUSTSTORE_BUCKET)
        # s3_client.put_object("")  # certs and keys

        from etl.sds.trigger.update import update

        update.cache["S3_CLIENT"] = s3_client
        response = update.handler()

    assert response == "abc"


@pytest.mark.integration
def test_update_integration():
    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(FunctionName=function_name)
    assert response["StatusCode"] == 200
    assert response["Payload"] == "abc"
