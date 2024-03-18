import os
from unittest import mock

from moto import mock_aws


def test_correct_apikey():
    with mock_aws(), mock.patch.dict(os.environ, {"ENVIRONMENT": "dev"}, clear=True):
        import api.authoriser.index as index

        index.CLIENT.create_secret(
            Name="dev-apigee-cpm-apikey",
            SecretString="hello",  # pragma: allowlist secret
        )

        apikey = "hello"  # pragma: allowlist secret

        result = index.handler(
            event={"methodArn": "foo", "headers": {"apikey": apikey}}
        )

    assert result == {
        "principalId": index.__file__,
        "context": {},
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "foo",
                }
            ],
        },
    }


def test_incorrect_apikey():
    with mock_aws(), mock.patch.dict(os.environ, {"ENVIRONMENT": "dev"}, clear=True):
        import api.authoriser.index as index

        index.CLIENT.create_secret(
            Name="dev-apigee-cpm-apikey",
            SecretString="hello",  # pragma: allowlist secret
        )

        apikey = "not-hello"  # pragma: allowlist secret

        result = index.handler(
            event={"methodArn": "foo", "headers": {"apikey": apikey}}
        )

    assert result == {
        "principalId": index.__file__,
        "context": {
            "error": "Provided apikey in request does not match the Connecting Party Manager apikey"
        },
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": "foo",
                }
            ],
        },
    }
